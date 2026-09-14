/**
 * 家庭保险管理系统 - 通用工具函数模块
 */

/**
 * 格式化金额为千分位形式 (如 6,942.43)
 */
export function formatMoney(val) {
  if (val === undefined || val === null || isNaN(val)) return '0.00';
  return Number(val).toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
}

/**
 * 根据险种分类返回对应的 Tailwind 徽章样式类
 */
export function getTypeBadgeClass(type) {
  if (!type) return 'bg-slate-100 text-slate-700';
  if (type.includes('车险')) {
    return 'bg-teal-50 text-teal-800 border border-teal-200/80 font-bold';
  }
  if (type.includes('重疾') || type.includes('寿险')) {
    return 'bg-amber-50 text-amber-700 border border-amber-200/60';
  }
  if (type.includes('医疗')) {
    return 'bg-sky-50 text-sky-700 border border-sky-200/60';
  }
  if (type.includes('意外')) {
    return 'bg-emerald-50 text-emerald-700 border border-emerald-200/60';
  }
  return 'bg-purple-50 text-purple-700 border border-purple-200/60';
}

export const DEFAULT_PHONE_CONFIG = {
  defaultPhone: '',
  phones: [
    { id: 'phone_1', name: '中国平安', keyword: '平安', phone: '95511', notes: '全国统一客服与理赔报案（产险/寿险/健康险）' },
    { id: 'phone_2', name: '中国人保', keyword: '人保', phone: '95518', notes: 'PICC 中国人保全国客服热线' },
    { id: 'phone_3', name: '中国人寿', keyword: '人寿', phone: '95519', notes: '中国人寿全国统一客户服务专线' },
    { id: 'phone_4', name: '中国太保', keyword: '太保', phone: '95500', notes: '太平洋人寿/财险全国统一热线' },
    { id: 'phone_5', name: '华夏保险', keyword: '华夏', phone: '95300', notes: '华夏人寿全国客户服务热线' },
    { id: 'phone_6', name: '众安保险', keyword: '众安', phone: '1010-9955', notes: '众安互联网财险全国客服专线' },
    { id: 'phone_7', name: '大都会人寿', keyword: '大都会', phone: '400-818-8168', notes: '中美联泰大都会人寿全国热线' },
    { id: 'phone_8', name: '绍兴市民保/人社', keyword: '绍兴政府', phone: '12333', notes: '绍兴市民保 / 全国人社政务服务便民热线' },
    { id: 'phone_9', name: '中华联合保险', keyword: '中华', phone: '95585', notes: '中华财险/人寿全国客户服务电话' },
    { id: 'phone_10', name: '中国大地保险', keyword: '大地', phone: '95590', notes: '大地财险客户服务及报案专线' },
    { id: 'phone_11', name: '阳光保险', keyword: '阳光', phone: '95510', notes: '阳光财险/人寿客户服务电话' },
    { id: 'phone_12', name: '中国太平', keyword: '太平', phone: '95589', notes: '太平人寿/财险全国客户服务热线' }
  ]
};

/**
 * 根据保险公司名称查询客服/报案电话
 * 支持传入动态配置或使用默认预设
 */
export function getCompanyPhone(company, config = null) {
  const cfg = config && typeof config === 'object' ? config : DEFAULT_PHONE_CONFIG;
  const list = Array.isArray(cfg) ? cfg : (cfg.phones || DEFAULT_PHONE_CONFIG.phones);
  const fallback = (cfg && cfg.defaultPhone !== undefined) ? cfg.defaultPhone : DEFAULT_PHONE_CONFIG.defaultPhone;

  if (!company) return fallback;

  for (const item of list) {
    if (item && item.keyword && company.includes(item.keyword)) {
      return item.phone;
    }
  }
  return fallback;
}


/**
 * 获取今天 YYYY-MM-DD 字符串
 */
export function getTodayStr() {
  return new Date().toISOString().slice(0, 10);
}

/**
 * 深度克隆对象
 */
export function deepClone(obj) {
  if (!obj) return obj;
  try {
    return JSON.parse(JSON.stringify(obj));
  } catch (e) {
    return { ...obj };
  }
}

/**
 * 纯原生浏览器下载文件辅助函数
 */
export function downloadFile(content, fileName, mimeType = 'text/plain;charset=utf-8') {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = fileName;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
