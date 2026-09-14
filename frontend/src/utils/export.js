/**
 * 家庭保险管理系统 - 数据备份与日历导出模块
 * 零三方大库依赖，纯原生 JSON 导出/导入与 iCal (.ics) 日历订阅
 */
import { downloadFile, getTodayStr } from './helpers.js';

/**
 * 导出全量家庭保险数据为标准 JSON 备份文件
 * @param {Object} fullData 包含 policies, paymentRecords, members 等完整数据
 */
export function exportToJson(fullData) {
  const exportPayload = {
    version: '2.0',
    exportedAt: new Date().toISOString(),
    data: fullData
  };
  const content = JSON.stringify(exportPayload, null, 2);
  const fileName = `family_insurance_backup_${getTodayStr()}.json`;
  downloadFile(content, fileName, 'application/json;charset=utf-8');
}

/**
 * 读取用户本地选择的 JSON 备份文件并解析校验
 * @param {File} file 本地上传文件
 * @returns {Promise<Object>} 解析后的保险数据对象
 */
export function importFromJson(file) {
  return new Promise((resolve, reject) => {
    if (!file) {
      return reject(new Error('未选择任何文件'));
    }
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const json = JSON.parse(e.target.result);
        const payload = json.data || json;
        if (!payload.policies && !Array.isArray(payload)) {
          throw new Error('未识别的 JSON 备份格式，需包含 policies 保单列表');
        }
        resolve(payload);
      } catch (err) {
        reject(new Error('JSON 文件解析失败: ' + err.message));
      }
    };
    reader.onerror = () => reject(new Error('文件读取失败'));
    reader.readAsText(file);
  });
}

/**
 * 导出当前生效在缴保单为 iCalendar (.ics) 日历日程文件
 * 支持一键导入 Apple 日历、Google Calendar、Outlook 等
 * @param {Array} activePolicies 正常在保的保单列表
 */
export function exportToICS(activePolicies = []) {
  const today = new Date();
  const currentYear = today.getFullYear();
  const ics = [
    'BEGIN:VCALENDAR',
    'VERSION:2.0',
    'PRODID:-//Family Insurance Manager//CN',
    'CALSCALE:GREGORIAN',
    'METHOD:PUBLISH',
    'X-WR-CALNAME:家庭保费缴费提醒',
    'X-WR-TIMEZONE:Asia/Shanghai'
  ];

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
    const monthStr = String(month).padStart(2, '0');
    const dayStr = String(day).padStart(2, '0');
    const startStr = `${currentYear}${monthStr}${dayStr}T090000`;
    const endStr = `${currentYear}${monthStr}${dayStr}T100000`;
    const uid = `policy-${p.id}-${currentYear}@family-insurance`;

    ics.push(
      'BEGIN:VEVENT',
      `UID:${uid}`,
      `DTSTAMP:${startStr}Z`,
      `DTSTART:${startStr}`,
      `DTEND:${endStr}`,
      `SUMMARY:【保费扣缴】${p.member} - ${p.name} (¥${p.premium})`,
      `DESCRIPTION:被保人: ${p.member}\\n险种: ${p.type}\\n保险公司: ${p.company}\\n应缴金额: ¥${p.premium}\\n保额: ${p.amount}`,
      'BEGIN:VALARM',
      'ACTION:DISPLAY',
      'DESCRIPTION:保费即将扣缴提醒',
      'TRIGGER:-P3D',
      'END:VALARM',
      'END:VEVENT'
    );
  });

  ics.push('END:VCALENDAR');
  const content = ics.join('\r\n');
  downloadFile(content, `family_insurance_calendar_${currentYear}.ics`, 'text/calendar;charset=utf-8');
}
