/**
 * 家庭保险管理系统 - API 通信与鉴权降级层
 * 统一管理 HTTP 请求拦截、Token 持久化与离线静态平滑回退
 */

const TOKEN_KEY = 'family_insurance_token';
const CACHE_KEY = 'family_insurance_data';
const PHONE_CACHE_KEY = 'family_insurance_phones';

let unauthorizedListeners = [];

/**
 * 本地缓存安全存储辅助方法，防范浏览器 5MB 配额异常
 */
function safeSetItem(key, val) {
  try {
    localStorage.setItem(key, val);
  } catch (err) {
    console.warn('[Storage] 本地离线缓存容量超限，跳过本地副本写入，不影响服务端保存:', err);
  }
}

export const AppApi = {
  onUnauthorized(callback) {
    if (typeof callback === 'function') {
      unauthorizedListeners.push(callback);
    }
  },

  notifyUnauthorized() {
    this.clearToken();
    unauthorizedListeners.forEach(cb => {
      try { cb(); } catch (e) { console.error(e); }
    });
  },

  getToken() {
    return localStorage.getItem(TOKEN_KEY) || '';
  },

  setToken(token) {
    if (token) {
      safeSetItem(TOKEN_KEY, token);
    } else {
      localStorage.removeItem(TOKEN_KEY);
    }
  },

  clearToken() {
    localStorage.removeItem(TOKEN_KEY);
  },

  clearLocalCache() {
    localStorage.removeItem(CACHE_KEY);
    localStorage.removeItem(PHONE_CACHE_KEY);
  },

  /**
   * 统一附带 Bearer Token 的 Fetch 封装
   */
  async fetchWithAuth(url, options = {}) {
    options.headers = options.headers || {};
    const token = this.getToken();
    if (token) {
      options.headers['Authorization'] = `Bearer ${token}`;
    }
    const res = await fetch(url, options);
    if (res.status === 401) {
      this.notifyUnauthorized();
      const err = new Error('UNAUTHORIZED');
      err.status = 401;
      throw err;
    }
    return res;
  },

  /**
   * 查询服务端密码保护开启状态及当前 Token 有效性
   */
  async checkAuthStatus() {
    try {
      const headers = {};
      const token = this.getToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      const res = await fetch('/api/auth/status', { headers });
      if (res.ok) {
        const resData = await res.json();
        return {
          authRequired: !!resData.auth_required,
          authenticated: !!resData.authenticated
        };
      }
    } catch (e) {
      console.warn('[API] Auth check skipped (offline mode):', e);
    }
    return { authRequired: false, authenticated: true };
  },

  /**
   * 提交访问密码换取 Token
   */
  async login(password) {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password })
    });
    const json = await res.json();
    if (res.ok && json.token) {
      this.setToken(json.token);
      return { success: true, token: json.token };
    }
    return {
      success: false,
      error: json.error || '访问密码错误，请重新输入'
    };
  },

  /**
   * 加载全量家庭保单与流水数据 (支持平滑离线降级)
   */
  async loadData() {
    try {
      const res = await this.fetchWithAuth('/api/data');
      if (res.ok) {
        const resJson = await res.json();
        if (!resJson.paymentRecords) {
          resJson.paymentRecords = { updatedAt: '', confirmations: {}, archiveRecords: [] };
        }
        // 缓存至本地存储，保障断网可用
        safeSetItem(CACHE_KEY, JSON.stringify(resJson));
        return { data: resJson, isApiConnected: true };
      }
      throw new Error('API request failed');
    } catch (e) {
      if (e.message === 'UNAUTHORIZED') {
        throw e;
      }

      console.warn('[API] 后端接口访问受限，读取本地离线缓存...');
      let fallbackData = {
        updatedAt: '',
        members: [],
        memberSummary: {},
        familyMembers: [],
        policies: [],
        vehicles: [],
        companies: [],
        paymentRecords: { updatedAt: '', confirmations: {}, archiveRecords: [] }
      };

      const localStr = localStorage.getItem(CACHE_KEY);
      if (localStr) {
        try {
          fallbackData = JSON.parse(localStr);
        } catch (_) {}
      }

      return { data: fallbackData, isApiConnected: false };
    }
  },

  /**
   * 加载保险服务与报案电话配置
   */
  async loadInsurancePhones() {
    try {
      const res = await this.fetchWithAuth('/api/insurance-phones');
      if (res.ok) {
        const json = await res.json();
        safeSetItem(PHONE_CACHE_KEY, JSON.stringify(json));
        return json;
      }
    } catch (e) {
      console.warn('[API] 读取保险电话配置接口受限，尝试读取本地缓存:', e);
    }
    const cached = localStorage.getItem(PHONE_CACHE_KEY);
    if (cached) {
      try {
        return JSON.parse(cached);
      } catch (_) {}
    }
    return null;
  },

  /**
   * 保存保险服务与报案电话配置
   */
  async saveInsurancePhones(payload) {
    safeSetItem(PHONE_CACHE_KEY, JSON.stringify(payload));
    const res = await this.fetchWithAuth('/api/insurance-phones', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      throw new Error('Save insurance phones API returned error');
    }
    return await res.json();
  },

  /**
   * 加载关联企业与营业执照备查记录
   */
  async loadCompanies() {
    try {
      const res = await this.fetchWithAuth('/api/companies');
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      console.warn('[API] 读取企业资质备查记录受限:', e);
    }
    return { updatedAt: '', companies: [] };
  },

  /**
   * 保存关联企业与营业执照备查记录
   */
  async saveCompanies(payload) {
    const res = await this.fetchWithAuth('/api/companies', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      throw new Error('Save companies API returned error');
    }
    return await res.json();
  },

  /**
   * 保存全量数据至服务端落盘 (同时写入 localStorage 双重保险)
   */
  async saveData(payload) {
    safeSetItem(CACHE_KEY, JSON.stringify(payload));
    const res = await this.fetchWithAuth('/api/data', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      throw new Error('Save API returned error');
    }
    return await res.json();
  },

  /**
   * 单笔更新或核销缴费状态
   */
  async confirmPaymentRecord(recordKey, conf) {
    return await this.fetchWithAuth('/api/payment-records/confirm', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ recordKey, ...conf })
    });
  },

  /**
   * 上传文件附件 (支持 PDF、图片，支持指定子归档目录)
   * 采用原生 FormData 流式直传，告别大文件 Base64 编码掉帧与内存膨胀
   */
  async uploadAttachment(category, file, subfolder = '') {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', category || 'personal');
    formData.append('subfolder', subfolder || '');

    const res = await this.fetchWithAuth('/api/attachments/upload', {
      method: 'POST',
      body: formData
    });
    if (!res.ok) {
      throw new Error(`Upload failed: ${res.status}`);
    }
    const json = await res.json();
    return json.attachment;
  },

  /**
   * 删除指定附件
   */
  async deleteAttachment(category, filename) {
    const res = await this.fetchWithAuth('/api/attachments/delete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        category: category || 'personal',
        filename
      })
    });
    return res.ok;
  },

  /**
   * 扫描孤儿附件状态与列表
   */
  async getOrphanAttachments() {
    const res = await this.fetchWithAuth('/api/attachments/orphans');
    if (!res.ok) throw new Error('扫描孤儿附件失败');
    return await res.json();
  },

  /**
   * 执行安全清理所有孤儿附件
   */
  async cleanOrphanAttachments() {
    const res = await this.fetchWithAuth('/api/attachments/orphans/clean', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    });
    if (!res.ok) throw new Error('清理孤儿附件失败');
    return await res.json();
  }
};

/**
 * 辅助获取带凭证参数的附件静态链接，以便在 <a> 标签新窗口打开或 <img> 中直接展示
 */
export function getAttachmentUrl(url) {
  if (!url) return '';
  const safeUrl = encodeURI(url);
  const token = AppApi.getToken();
  if (!token) return safeUrl;
  const separator = safeUrl.includes('?') ? '&' : '?';
  return `${safeUrl}${separator}token=${encodeURIComponent(token)}`;
}
