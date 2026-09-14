import { ref, computed } from 'vue';
import { AppApi } from '../api/index.js';

// 模块级单例状态：热模块替换（HMR）时保持持久，不随组件 reload 重置
const authReady = ref(false);
const authToken = ref(AppApi.getToken());
const authState = ref({
  required: false,
  authenticated: false,
  password: '',
  loading: false,
  error: '',
  showPassword: false
});

const isSystemUnlocked = computed(() => {
  return authReady.value && (!authState.value.required || authState.value.authenticated);
});

let globalSecurityClear = null;
let globalToast = null;
let isUnauthorizedListenerBound = false;

function bindUnauthorizedListenerOnce() {
  if (isUnauthorizedListenerBound) return;
  AppApi.onUnauthorized(() => {
    if (authState.value.required) {
      if (globalSecurityClear) globalSecurityClear();
      authToken.value = '';
      authState.value.authenticated = false;
      if (globalToast) {
        globalToast('访问凭证已失效，系统已自动锁定保护', 'error');
      }
    }
  });
  isUnauthorizedListenerBound = true;
}

export function useAuth({ onLoginSuccess, onSecurityClear, showToast } = {}) {
  if (onSecurityClear) globalSecurityClear = onSecurityClear;
  if (showToast) globalToast = showToast;
  bindUnauthorizedListenerOnce();

  const checkAuth = async () => {
    const status = await AppApi.checkAuthStatus();
    authState.value.required = status.authRequired;
    authState.value.authenticated = status.authenticated;
    return status;
  };

  const handleLogin = async () => {
    if (!authState.value.password) {
      authState.value.error = '请输入访问密码';
      return;
    }
    authState.value.loading = true;
    authState.value.error = '';

    try {
      const res = await AppApi.login(authState.value.password);
      if (res.success) {
        authToken.value = res.token;
        authState.value.authenticated = true;
        authState.value.password = '';
        if (showToast) showToast('解锁成功，欢迎查阅家庭保险资产！');
        if (onLoginSuccess) {
          await onLoginSuccess();
        }
      } else {
        authState.value.error = res.error;
      }
    } catch (e) {
      authState.value.error = '网络请求失败，请检查服务状态';
    } finally {
      authState.value.loading = false;
    }
  };

  const handleLogout = () => {
    AppApi.clearToken();
    if (onSecurityClear) onSecurityClear();
    authToken.value = '';
    authState.value.authenticated = false;
    authState.value.password = '';
    authState.value.error = '';
    if (showToast) showToast('已锁定界面，隐私数据已全部销毁');
  };

  return {
    authReady,
    authToken,
    authState,
    isSystemUnlocked,
    checkAuth,
    handleLogin,
    handleLogout
  };
}
