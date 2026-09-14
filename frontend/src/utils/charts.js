/**
 * 家庭保险管理系统 - 图表可视化引擎模块
 * 依赖：Chart.js
 */
import {
  Chart,
  BarController,
  BarElement,
  CategoryScale,
  LinearScale,
  DoughnutController,
  ArcElement,
  Tooltip,
  Legend
} from 'chart.js';

// 按需注册所需控制器、图形图元与插件
Chart.register(
  BarController,
  BarElement,
  CategoryScale,
  LinearScale,
  DoughnutController,
  ArcElement,
  Tooltip,
  Legend
);

let trendChartInstance = null;
let memberPieChartInstance = null;

export const AppCharts = {
  /**
   * 渲染历年实缴保费趋势柱状图
   * @param {HTMLCanvasElement|string} canvasOrId Canvas 元素或 ID
   * @param {Array} allPaymentSchedule 缴费排期总表
   */
  renderTrendChart(canvasOrId, allPaymentSchedule = []) {
    const el = typeof canvasOrId === 'string' ? document.getElementById(canvasOrId) : canvasOrId;
    if (!el) return;

    const yearMap = {};
    allPaymentSchedule.forEach(s => {
      if (s.isPaid) {
        yearMap[s.year] = (yearMap[s.year] || 0) + s.premium;
      }
    });
    const years = Object.keys(yearMap).sort();
    const values = years.map(y => yearMap[y]);

    // 双重安全防护：既销毁引用变量，又释放 DOM Canvas 节点上的已有 Chart 实例
    const existing = Chart.getChart(el);
    if (existing) {
      existing.destroy();
    }
    if (trendChartInstance) {
      trendChartInstance.destroy();
      trendChartInstance = null;
    }

    trendChartInstance = new Chart(el, {
      type: 'bar',
      data: {
        labels: years.map(y => y + '年'),
        datasets: [{
          label: '年度实交保费 (元)',
          data: values,
          backgroundColor: '#0ea5e9',
          borderRadius: 6,
          barPercentage: 0.6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (c) => ' 实交: ¥' + Number(c.raw).toLocaleString('zh-CN', { minimumFractionDigits: 2 })
            }
          }
        },
        scales: {
          y: {
            grid: { color: '#f1f5f9' },
            ticks: {
              callback: (v) => '¥' + (v / 1000) + 'k'
            }
          },
          x: {
            grid: { display: false }
          }
        }
      }
    });
  },

  /**
   * 渲染家庭成员保费分布环形图
   * @param {HTMLCanvasElement|string} canvasOrId Canvas 元素或 ID
   * @param {Array} activePolicies 正常在缴保单列表
   */
  renderMemberPieChart(canvasOrId, activePolicies = []) {
    const el = typeof canvasOrId === 'string' ? document.getElementById(canvasOrId) : canvasOrId;
    if (!el) return;

    const memberMap = {};
    activePolicies.forEach(p => {
      const prem = Number(p.premium) || 0;
      if (p.isFamilyPolicy && Array.isArray(p.insuredMembers) && p.insuredMembers.length > 0) {
        if (p.premiumSplitMode === 'equal') {
          const splitAmount = prem / p.insuredMembers.length;
          p.insuredMembers.forEach(m => {
            memberMap[m] = (memberMap[m] || 0) + splitAmount;
          });
        } else {
          memberMap[p.member] = (memberMap[p.member] || 0) + prem;
        }
      } else {
        memberMap[p.member] = (memberMap[p.member] || 0) + prem;
      }
    });
    const members = Object.keys(memberMap);
    const values = members.map(m => memberMap[m]);

    const existing = Chart.getChart(el);
    if (existing) {
      existing.destroy();
    }
    if (memberPieChartInstance) {
      memberPieChartInstance.destroy();
      memberPieChartInstance = null;
    }

    memberPieChartInstance = new Chart(el, {
      type: 'doughnut',
      data: {
        labels: members,
        datasets: [{
          data: values,
          backgroundColor: ['#0284c7', '#38bdf8', '#818cf8', '#a855f7', '#f43f5e', '#10b981'],
          borderWidth: 2,
          borderColor: '#ffffff'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '70%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: { boxWidth: 10, font: { size: 11 } }
          },
          tooltip: {
            callbacks: {
              label: (c) => ` ${c.label}: ¥${Number(c.raw).toLocaleString('zh-CN', { minimumFractionDigits: 2 })}`
            }
          }
        }
      }
    });
  },

  /**
   * 销毁现有所有图表实例，释放内存
   */
  destroyAll() {
    if (trendChartInstance) {
      trendChartInstance.destroy();
      trendChartInstance = null;
    }
    if (memberPieChartInstance) {
      memberPieChartInstance.destroy();
      memberPieChartInstance = null;
    }
  }
};
