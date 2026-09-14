/**
 * 辅助函数：从车辆对象中标准化提取历年车险记录列表（兼容老版本内嵌结构）
 */
export function extractVehicleInsuranceRecords(v) {
  if (!v) return [];
  let list = [];
  if (Array.isArray(v.insuranceRecords)) {
    list = v.insuranceRecords;
  } else {
    // 兼容历史老版本内嵌结构（仅当 insuranceRecords 字段未定义时回退）
    const comm = v.commercialInsurance || {};
    const comp = v.compulsoryInsurance || {};
    const sDate = comm.startDate || comp.startDate;
    if (sDate && (comm.company || comp.company || comm.premium || comp.premium)) {
      const yr = parseInt(sDate.slice(0, 4), 10) || new Date().getFullYear();
      const cPrem = Number(comm.premium || 0);
      const compPrem = Number(comp.premium || 0);
      const tax = Number(comp.tax || 0);
      list = [{
        id: `rec_${v.id}_${yr}`,
        vehicleId: v.id,
        year: yr,
        company: comm.company || comp.company || '',
        commercialPolicyNo: comm.policyNo || '',
        compulsoryPolicyNo: comp.policyNo || '',
        commercialPremium: cPrem,
        compulsoryPremium: compPrem,
        tax: tax,
        totalPremium: cPrem + compPrem + tax,
        startDate: sDate,
        endDate: comm.endDate || comp.endDate || '',
        dueDate: sDate,
        thirdPartyAmount: comm.thirdPartyAmount || '300万',
        hasDamage: comm.hasDamage !== false,
        hasMedicalExcluded: !!comm.hasMedicalExcluded,
        driverAmount: comm.driverAmount || '',
        attachments: v.attachments || [],
        remark: v.remark || ''
      }];
    }
  }

  return list.map(rec => {
    const cPrem = Number(rec.commercialPremium !== undefined ? rec.commercialPremium : (rec.commercialInsurance?.premium || 0));
    const compPrem = Number(rec.compulsoryPremium !== undefined ? rec.compulsoryPremium : (rec.compulsoryInsurance?.premium || 0));
    const tax = Number(rec.tax !== undefined ? rec.tax : (rec.compulsoryInsurance?.tax || 0));
    const accidentPrem = Number(rec.accidentPremium !== undefined ? rec.accidentPremium : 0);
    const total = Number(rec.totalPremium) || (cPrem + compPrem + tax + accidentPrem);
    const sDate = rec.startDate || rec.commercialInsurance?.startDate || rec.compulsoryInsurance?.startDate || '';
    const yr = Number(rec.year) || (sDate ? parseInt(sDate.slice(0, 4), 10) : new Date().getFullYear());
    const eDate = rec.endDate || rec.commercialInsurance?.endDate || rec.compulsoryInsurance?.endDate || '';
    return {
      ...rec,
      id: rec.id || `rec_${v.id}_${yr}`,
      vehicleId: rec.vehicleId || v.id,
      year: yr,
      company: rec.company || rec.commercialInsurance?.company || rec.compulsoryInsurance?.company || '',
      commercialPolicyNo: rec.commercialPolicyNo || rec.commercialInsurance?.policyNo || '',
      compulsoryPolicyNo: rec.compulsoryPolicyNo || rec.compulsoryInsurance?.policyNo || '',
      accidentPolicyNo: rec.accidentPolicyNo || '',
      commercialPremium: cPrem,
      compulsoryPremium: compPrem,
      tax: tax,
      accidentPremium: accidentPrem,
      cashback: Number(rec.cashback || 0),
      totalPremium: total,
      startDate: sDate,
      endDate: eDate,
      dueDate: rec.dueDate || sDate || `${yr}-01-01`,
      thirdPartyAmount: rec.thirdPartyAmount || rec.commercialInsurance?.thirdPartyAmount || '300万',
      hasDamage: rec.hasDamage !== undefined ? rec.hasDamage : (rec.commercialInsurance?.hasDamage !== false),
      hasMedicalExcluded: rec.hasMedicalExcluded !== undefined ? rec.hasMedicalExcluded : !!rec.commercialInsurance?.hasMedicalExcluded,
      driverAmount: rec.driverAmount || rec.commercialInsurance?.driverAmount || '',
      attachments: rec.attachments || [],
      remark: rec.remark || ''
    };
  }).sort((a, b) => (b.year || 0) - (a.year || 0));
}

export const PaymentScheduleEngine = {
  /**
   * 生成完整的历史与未来缴费台账列表 (按应缴日期倒序)
   * 现已全面整合商业保单与历年车险保单
   */
  generateSchedule(policies, paymentRecords, today = new Date(), vehicles = []) {
    const schedule = [];
    const todayStr = today.toISOString().slice(0, 10);
    const currentYear = today.getFullYear();
    const confirmations = paymentRecords?.confirmations || {};

    // 1. 遍历人身与商业保单推算全部历史和应缴排期
    (policies || []).forEach(p => {
      const startStr = p.startDate || (p.coverageDates ? p.coverageDates.split('~')[0].trim() : '') || '2020-01-01';
      const startYear = parseInt(startStr.slice(0, 4), 10) || 2020;
      const pYears = Number(p.paymentYears) || 1;
      const monthDay = p.paymentMonthDay || (startStr.length >= 10 ? startStr.slice(5) : '01-01');
      const isShortTerm = pYears === 1;

      // 获取当前保单在 confirmations 中已存在的最小与最大年份（向下兼容历史补录、向上支持未来年份）
      const confYears = Object.keys(confirmations)
        .filter(k => k.startsWith(`p_${p.id}_`))
        .map(k => parseInt(k.split('_')[2], 10))
        .filter(yr => !isNaN(yr));
      const minConfYear = confYears.length > 0 ? Math.min(...confYears) : startYear;
      const maxConfYear = confYears.length > 0 ? Math.max(...confYears) : 0;
      const effectiveStartYear = Math.min(startYear, minConfYear);

      // 计算终止年份：
      // 1年期短期连续保单：若保单有效在保 (status === 'active')，自动预测至下一年 (currentYear + 1)，同时兼容已有手动记录的最大年份
      let endYear = isShortTerm
        ? (p.status === 'active' ? Math.max(currentYear + 1, maxConfYear) : Math.max(currentYear, maxConfYear))
        : Math.max(startYear + pYears - 1, maxConfYear);
      if (p.status === 'stopped' && p.stopYear) {
        endYear = Math.min(endYear, p.stopYear);
      }

      for (let y = effectiveStartYear; y <= endYear; y++) {
        const recKey = `p_${p.id}_${y}`;
        const conf = confirmations[recKey];

        // 若显式标记断缴/删除（skipped 或 deleted），则从台账中彻底剔除该年份
        if (conf && (conf.skipped === true || conf.deleted === true)) {
          continue;
        }

        const dueDate = `${y}-${monthDay}`;
        const periodIndex = y - effectiveStartYear + 1;
        const totalPeriods = pYears;

        // 核心理念：到期自动扣款，除非被显式标记为扣款失败/未缴 (conf.paid === false)
        const isExplicitUnpaid = conf && conf.paid === false;
        const isExplicitPaid = conf && conf.paid === true;
        const isArrived = dueDate <= todayStr;

        let isPaid = false;
        let status = 'upcoming';

        if (isExplicitUnpaid) {
          isPaid = false;
          status = 'unpaid'; // 扣费异常/未成功扣款
        } else if (isExplicitPaid || isArrived) {
          // 到期自动视为已自动代扣成功，或已被显式确认
          isPaid = true;
          status = 'paid';
        } else {
          isPaid = false;
          status = 'upcoming'; // 未到扣费日
        }

        // 计算距今天数（用于近期待扣提醒）
        let diffDays = 0;
        let isNearUpcoming = false;
        if (status === 'upcoming') {
          const dueTime = new Date(dueDate).getTime();
          const todayTime = new Date(todayStr).getTime();
          diffDays = Math.ceil((dueTime - todayTime) / (1000 * 60 * 60 * 24));
          isNearUpcoming = diffDays >= 0 && diffDays <= 30;
        }

        const standardPremium = Number(p.premium) || 0;
        const actualPaidAmount = (conf?.paidAmount !== undefined && conf?.paidAmount !== null && conf?.paidAmount !== '')
          ? Number(conf.paidAmount)
          : standardPremium;

        // 实缴状态下若有实缴金额，以实缴为准；未到期则取保单标保
        const effectivePremium = isPaid ? actualPaidAmount : standardPremium;

        schedule.push({
          key: recKey,
          policyId: p.id,
          year: y,
          dueDate: dueDate,
          periodIndex: periodIndex,
          totalPeriods: totalPeriods,
          isShortTerm: isShortTerm,
          member: p.member,
          isFamilyPolicy: !!p.isFamilyPolicy,
          insuredMembers: Array.isArray(p.insuredMembers) ? p.insuredMembers : (p.member ? [p.member] : []),
          premiumSplitMode: p.premiumSplitMode || 'payer',
          type: p.type,
          name: p.name,
          company: p.company,
          amount: p.amount,
          premium: effectivePremium,
          standardPremium: standardPremium,
          paidAmount: actualPaidAmount,
          hasCustomAmount: isPaid && Math.abs(actualPaidAmount - standardPremium) > 0.001,
          status: status,
          isPaid: isPaid,
          isExplicitUnpaid: isExplicitUnpaid,
          isNearUpcoming: isNearUpcoming,
          diffDays: diffDays,
          paidDate: conf?.paidDate || (isPaid ? dueDate : ''),
          note: conf?.note || (isExplicitUnpaid ? '标记扣款失败' : (isPaid ? '银行自动代扣' : '')),
          confirmedAt: conf?.confirmedAt || '',
          policyStatus: p.status,
          isVehicle: false,
          isArchive: false
        });
      }
    });

    // 2. 遍历车辆与历年车险记录（车险录入即代表已出单付款，默认天然已缴）
    (vehicles || []).forEach(v => {
      const records = extractVehicleInsuranceRecords(v);
      records.forEach(rec => {
        const y = rec.year || parseInt((rec.startDate || todayStr).slice(0, 4), 10);
        const recKey = `v_${v.id}_${y}`;
        const dueDate = rec.dueDate || rec.startDate || `${y}-01-01`;
        const totalPrem = Number(rec.totalPremium || (Number(rec.commercialPremium || 0) + Number(rec.compulsoryPremium || 0) + Number(rec.tax || 0) + Number(rec.accidentPremium || 0)));

        const conf = confirmations[recKey];
        if (conf && (conf.skipped === true || conf.deleted === true)) {
          return;
        }

        const isExplicitUnpaid = conf && conf.paid === false;
        const actualPaidAmount = (conf?.paidAmount !== undefined && conf?.paidAmount !== null && conf?.paidAmount !== '')
          ? Number(conf.paidAmount)
          : totalPrem;

        let isPaid = true;
        let status = 'paid';

        if (isExplicitUnpaid) {
          isPaid = false;
          status = 'unpaid';
        } else {
          isPaid = true;
          status = 'paid';
        }

        schedule.push({
          key: recKey,
          policyId: `v_${v.id}`,
          isVehicle: true,
          vehicleId: v.id,
          plateNo: v.plateNo,
          plateType: v.plateType || 'blue',
          year: y,
          dueDate: dueDate,
          periodIndex: 1,
          totalPeriods: 1,
          isShortTerm: true,
          member: v.owner,
          type: '车险',
          name: `${v.plateNo} 车险 (${v.model})`,
          company: rec.company,
          amount: rec.thirdPartyAmount ? `三者${rec.thirdPartyAmount}` : '机动车综合险',
          premium: actualPaidAmount,
          standardPremium: totalPrem,
          paidAmount: actualPaidAmount,
          hasCustomAmount: isPaid && Math.abs(actualPaidAmount - totalPrem) > 0.001,
          status: status,
          isPaid: isPaid,
          isExplicitUnpaid: isExplicitUnpaid,
          isNearUpcoming: false,
          diffDays: 0,
          paidDate: conf?.paidDate || dueDate,
          note: conf?.note || rec.remark || '录入已支付',
          confirmedAt: conf?.confirmedAt || '',
          policyStatus: 'active',
          isArchive: false
        });
      });
    });

    // 3. 合并历史归档保单流水 (早期已结清停售产品)
    const archives = paymentRecords?.archiveRecords || [];
    archives.forEach(arch => {
      const conf = confirmations[arch.id];
      // 若显式标记断缴/删除（skipped 或 deleted），则从台账中彻底剔除
      if (conf && (conf.skipped === true || conf.deleted === true)) {
        return;
      }

      const dueDate = conf?.paidDate || arch.paymentDate;
      const isExplicitUnpaid = conf && conf.paid === false;
      const isPaid = isExplicitUnpaid ? false : (conf?.paid !== undefined ? conf.paid : (arch.paid !== false));
      const status = isPaid ? 'paid' : 'unpaid';
      const actualPremium = conf?.paidAmount !== undefined ? Number(conf.paidAmount) : (Number(arch.premium) || 0);

      schedule.push({
        key: arch.id,
        policyId: 0,
        year: conf?.year || arch.year,
        dueDate: dueDate,
        periodIndex: 1,
        totalPeriods: 1,
        isShortTerm: true,
        member: arch.member,
        type: arch.type,
        name: arch.name,
        company: arch.company,
        amount: arch.amount,
        premium: actualPremium,
        standardPremium: Number(arch.premium) || actualPremium,
        paidAmount: actualPremium,
        status: status,
        isPaid: isPaid,
        isExplicitUnpaid: isExplicitUnpaid,
        isNearUpcoming: false,
        diffDays: 0,
        paidDate: isPaid ? dueDate : '',
        note: conf?.note || arch.note || '历史归档保单',
        confirmedAt: conf?.confirmedAt || arch.paymentDate,
        policyStatus: 'stopped',
        isVehicle: false,
        isArchive: true
      });
    });

    // 默认按扣缴日期倒序排列 (最新在前)
    return schedule.sort((a, b) => b.dueDate.localeCompare(a.dueDate));
  },

  /**
   * 缴费日历分组：按 1~12 月展示并关联当月缴费确认状态 (全面支持车险)
   */
  generateCalendarGroups(activePolicies, paymentRecords, today = new Date(), vehicles = []) {
    const map = {};
    const currentYear = today.getFullYear();
    const todayStr = today.toISOString().slice(0, 10);
    const confirmations = paymentRecords?.confirmations || {};

    // 1. 放入商业险保单
    (activePolicies || []).forEach(p => {
      let month = 1;
      let day = 1;
      if (p.paymentMonthDay && p.paymentMonthDay.includes('-')) {
        const parts = p.paymentMonthDay.split('-');
        month = parseInt(parts[0], 10);
        day = parseInt(parts[1], 10);
      } else if (p.startDate) {
        const parts = p.startDate.split('-');
        if (parts.length >= 3) {
          month = parseInt(parts[1], 10);
          day = parseInt(parts[2], 10);
        }
      }

      const recKey = `p_${p.id}_${currentYear}`;
      const conf = confirmations[recKey];
      const dueDate = `${currentYear}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
      const isExplicitUnpaid = conf && conf.paid === false;
      const isPaid = !isExplicitUnpaid && (conf?.paid === true || dueDate <= todayStr);
      const isUnpaid = isExplicitUnpaid;
      const isUpcoming = !isPaid && !isUnpaid;

      if (!map[month]) map[month] = [];
      map[month].push({
        ...p,
        isVehicle: false,
        paymentMonth: month,
        paymentDay: day,
        currentYearPaid: isPaid,
        isUnpaid: isUnpaid,
        isUpcoming: isUpcoming,
        isDuePending: false // 废除待核实红点
      });
    });

    // 2. 放入当前年度或最近一期车险（车险默认已缴）
    (vehicles || []).forEach(v => {
      const records = extractVehicleInsuranceRecords(v);
      // 优先取今年记录，没有则取最新一期
      const currentRec = records.find(r => r.year === currentYear) || records[records.length - 1];
      if (!currentRec || !currentRec.startDate) return;

      let month = 1;
      let day = 1;
      const parts = currentRec.startDate.split('-');
      if (parts.length >= 3) {
        month = parseInt(parts[1], 10);
        day = parseInt(parts[2], 10);
      }

      const recKey = `v_${v.id}_${currentYear}`;
      const conf = confirmations[recKey];
      const dueDate = `${currentYear}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
      const isExplicitUnpaid = conf && conf.paid === false;
      const isPaid = !isExplicitUnpaid;
      const totalPrem = Number(currentRec.totalPremium || (Number(currentRec.commercialPremium || 0) + Number(currentRec.compulsoryPremium || 0) + Number(currentRec.tax || 0) + Number(currentRec.accidentPremium || 0)));

      if (!map[month]) map[month] = [];
      map[month].push({
        id: `v_${v.id}`,
        isVehicle: true,
        vehicleId: v.id,
        plateNo: v.plateNo,
        plateType: v.plateType,
        member: v.owner,
        name: `${v.plateNo} 车险 (${v.model})`,
        company: currentRec.company,
        type: '车险',
        amount: currentRec.thirdPartyAmount ? `三者${currentRec.thirdPartyAmount}` : '机动车综合险',
        premium: totalPrem,
        paymentMonth: month,
        paymentDay: day,
        currentYearPaid: isPaid,
        isUnpaid: isExplicitUnpaid,
        isUpcoming: false,
        isDuePending: false
      });
    });

    const res = [];
    Object.keys(map).sort((a, b) => Number(a) - Number(b)).forEach(m => {
      const items = map[m].sort((a, b) => a.paymentDay - b.paymentDay);
      const total = items.reduce((s, i) => s + (Number(i.premium) || 0), 0);
      res.push({ month: m, total, items });
    });
    return res;
  },


  /**
   * 根据多维度筛选条件过滤缴费流水
   */
  filterSchedule(allSchedule, filters = {}) {
    const {
      status = 'paid',
      year = '',
      member = '',
      type = '',
      search = '',
      selectedTargets = []
    } = filters;

    const q = (search || '').trim().toLowerCase();

    const filtered = (allSchedule || []).filter(item => {
      if (status === 'paid' && item.status !== 'paid') return false;
      if (status === 'upcoming' && item.status !== 'upcoming') return false;
      if ((status === 'unpaid' || status === 'due') && item.status !== 'unpaid') return false;
      if (year && item.year !== Number(year)) return false;
      if (member) {
        const isMatch = item.member === member ||
          (item.isFamilyPolicy && Array.isArray(item.insuredMembers) && item.insuredMembers.includes(member));
        if (!isMatch) return false;
      }

      // 多选缴费对象过滤 (人/车)
      if (Array.isArray(selectedTargets) && selectedTargets.length > 0) {
        const matchedTarget = selectedTargets.some(target => {
          if (target.type === 'member') {
            return !item.isVehicle && (
              item.member === target.value ||
              (item.isFamilyPolicy && Array.isArray(item.insuredMembers) && item.insuredMembers.includes(target.value))
            );
          }
          if (target.type === 'vehicle') {
            return item.isVehicle && item.plateNo === target.value;
          }
          return false;
        });
        if (!matchedTarget) return false;
      }

      if (type && !item.type.includes(type)) return false;
      if (q) {
        const matchInsured = item.isFamilyPolicy && Array.isArray(item.insuredMembers)
          ? item.insuredMembers.some(m => (m || '').toLowerCase().includes(q))
          : false;
        const matched =
          item.name.toLowerCase().includes(q) ||
          item.member.toLowerCase().includes(q) ||
          matchInsured ||
          item.company.toLowerCase().includes(q) ||
          (item.plateNo && item.plateNo.toLowerCase().includes(q));
        if (!matched) return false;
      }
      return true;
    });

    // 排序机制：预测 (upcoming) 按日期/年份正序 (由近及远)；已缴 (paid) 按日期倒序 (最新已缴在前)
    if (status === 'upcoming') {
      return [...filtered].sort((a, b) => a.dueDate.localeCompare(b.dueDate));
    }
    return [...filtered].sort((a, b) => b.dueDate.localeCompare(a.dueDate));
  }
};

