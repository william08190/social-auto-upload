<template>
  <div class="dashboard">
    <div class="page-header">
      <h1>自媒体自动化运营系统</h1>
    </div>
    
    <div class="dashboard-content">
      <el-row :gutter="20">
        <!-- 账号统计卡片 -->
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-card-content">
              <div class="stat-icon">
                <el-icon><User /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ accountStats.total }}</div>
                <div class="stat-label">账号总数</div>
              </div>
            </div>
            <div class="stat-footer">
              <div class="stat-detail">
                <span>正常: {{ accountStats.normal }}</span>
                <span>异常: {{ accountStats.abnormal }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <!-- 平台统计卡片 -->
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-card-content">
              <div class="stat-icon platform-icon">
                <el-icon><Platform /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ platformStats.total }}</div>
                <div class="stat-label">平台总数</div>
              </div>
            </div>
            <div class="stat-footer">
              <div class="stat-detail">
                <el-tooltip content="快手账号" placement="top">
                  <el-tag size="small" type="success">{{ platformStats.kuaishou }}</el-tag>
                </el-tooltip>
                <el-tooltip content="抖音账号" placement="top">
                  <el-tag size="small" type="danger">{{ platformStats.douyin }}</el-tag>
                </el-tooltip>
                <el-tooltip content="视频号账号" placement="top">
                  <el-tag size="small" type="warning">{{ platformStats.channels }}</el-tag>
                </el-tooltip>
                <el-tooltip content="小红书账号" placement="top">
                  <el-tag size="small" type="info">{{ platformStats.xiaohongshu }}</el-tag>
                </el-tooltip>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <!-- 素材统计卡片 -->
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-card-content">
              <div class="stat-icon task-icon">
                <el-icon><List /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ contentStats.total }}</div>
                <div class="stat-label">素材总数</div>
              </div>
            </div>
            <div class="stat-footer">
              <div class="stat-detail">
                <span>总大小: {{ contentStats.totalSize }} MB</span>
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- 存储统计卡片 -->
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-card-content">
              <div class="stat-icon content-icon">
                <el-icon><Document /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ contentStats.totalSize }}</div>
                <div class="stat-label">存储空间(MB)</div>
              </div>
            </div>
            <div class="stat-footer">
              <div class="stat-detail">
                <span>素材数: {{ contentStats.total }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- 快捷操作区域 -->
      <div class="quick-actions">
        <h2>快捷操作</h2>
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card class="action-card" @click="navigateTo('/account-management')">
              <div class="action-icon">
                <el-icon><UserFilled /></el-icon>
              </div>
              <div class="action-title">账号管理</div>
              <div class="action-desc">管理所有平台账号</div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="action-card" @click="navigateTo('/material-management')">
              <div class="action-icon">
                <el-icon><Upload /></el-icon>
              </div>
              <div class="action-title">素材管理</div>
              <div class="action-desc">上传和管理视频素材</div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="action-card" @click="navigateTo('/publish-center')">
              <div class="action-icon">
                <el-icon><Timer /></el-icon>
              </div>
              <div class="action-title">发布中心</div>
              <div class="action-desc">发布视频到各平台</div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="action-card" @click="refreshData">
              <div class="action-icon">
                <el-icon><DataAnalysis /></el-icon>
              </div>
              <div class="action-title">刷新数据</div>
              <div class="action-desc">刷新仪表盘统计数据</div>
            </el-card>
          </el-col>
        </el-row>
      </div>
      
      <!-- 最近上传的素材 -->
      <div class="recent-tasks">
        <div class="section-header">
          <h2>最近上传的素材</h2>
          <el-button text @click="navigateTo('/material-management')">查看全部</el-button>
        </div>

        <el-table :data="recentMaterials" style="width: 100%" v-if="recentMaterials.length > 0">
          <el-table-column prop="filename" label="文件名" width="300" />
          <el-table-column prop="filesize" label="大小(MB)" width="120" />
          <el-table-column prop="upload_time" label="上传时间" width="180" />
          <el-table-column label="操作">
            <template #default="scope">
              <el-button size="small" @click="viewMaterial(scope.row)">查看</el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-empty v-else description="暂无素材，请先上传" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  User, UserFilled, Platform, List, Document,
  Upload, Timer, DataAnalysis
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { accountApi } from '@/api/account'
import { materialApi } from '@/api/material'

const router = useRouter()

// API base URL
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5409'

// 账号统计数据
const accountStats = reactive({
  total: 0,
  normal: 0,
  abnormal: 0
})

// 平台统计数据
const platformStats = reactive({
  total: 4,
  kuaishou: 0,
  douyin: 0,
  channels: 0,
  xiaohongshu: 0
})

// 内容统计数据（素材）
const contentStats = reactive({
  total: 0,
  totalSize: 0
})

// 最近上传的素材
const recentMaterials = ref([])

// 获取仪表盘数据
const fetchDashboardData = async () => {
  try {
    // 获取账号数据
    const accountRes = await accountApi.getAccounts()
    if (accountRes.code === 200 && accountRes.data) {
      const accounts = accountRes.data

      // 计算账号统计
      accountStats.total = accounts.length
      accountStats.normal = accounts.filter(acc => acc[4] === 1).length
      accountStats.abnormal = accounts.filter(acc => acc[4] !== 1).length

      // 计算平台统计 (type: 1=小红书, 2=视频号, 3=抖音, 4=快手)
      platformStats.xiaohongshu = accounts.filter(acc => acc[1] === 1).length
      platformStats.channels = accounts.filter(acc => acc[1] === 2).length
      platformStats.douyin = accounts.filter(acc => acc[1] === 3).length
      platformStats.kuaishou = accounts.filter(acc => acc[1] === 4).length
    }

    // 获取素材数据
    const materialRes = await materialApi.getAllMaterials()
    if (materialRes.code === 200 && materialRes.data) {
      const materials = materialRes.data

      // 计算内容统计
      contentStats.total = materials.length
      contentStats.totalSize = materials.reduce((sum, m) => sum + (m.filesize || 0), 0).toFixed(2)

      // 获取最近5条素材作为最近上传
      recentMaterials.value = materials.slice(0, 5).map(m => ({
        id: m.id,
        filename: m.filename,
        filesize: m.filesize,
        upload_time: m.upload_time,
        file_path: m.file_path
      }))
    }
  } catch (error) {
    console.error('获取仪表盘数据失败:', error)
  }
}

// 页面加载时获取数据
onMounted(() => {
  fetchDashboardData()
})

// 根据平台获取标签类型
const getPlatformTagType = (platform) => {
  const typeMap = {
    '快手': 'success',
    '抖音': 'danger',
    '视频号': 'warning',
    '小红书': 'info'
  }
  return typeMap[platform] || 'info'
}

// 导航到指定路由
const navigateTo = (path) => {
  router.push(path)
}

// 刷新数据
const refreshData = () => {
  ElMessage.info('正在刷新数据...')
  fetchDashboardData().then(() => {
    ElMessage.success('数据刷新完成')
  })
}

// 查看素材详情
const viewMaterial = (material) => {
  // 跳转到素材管理页面
  router.push('/material-management')
}
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.dashboard {
  .page-header {
    margin-bottom: 20px;
    
    h1 {
      font-size: 24px;
      color: $text-primary;
      margin: 0;
    }
  }
  
  .dashboard-content {
    .stat-card {
      height: 140px;
      margin-bottom: 20px;
      
      .stat-card-content {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
        
        .stat-icon {
          width: 60px;
          height: 60px;
          border-radius: 50%;
          background-color: rgba($primary-color, 0.1);
          display: flex;
          justify-content: center;
          align-items: center;
          margin-right: 15px;
          
          .el-icon {
            font-size: 30px;
            color: $primary-color;
          }
          
          &.platform-icon {
            background-color: rgba($success-color, 0.1);
            
            .el-icon {
              color: $success-color;
            }
          }
          
          &.task-icon {
            background-color: rgba($warning-color, 0.1);
            
            .el-icon {
              color: $warning-color;
            }
          }
          
          &.content-icon {
            background-color: rgba($info-color, 0.1);
            
            .el-icon {
              color: $info-color;
            }
          }
        }
        
        .stat-info {
          .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: $text-primary;
            line-height: 1.2;
          }
          
          .stat-label {
            font-size: 14px;
            color: $text-secondary;
          }
        }
      }
      
      .stat-footer {
        border-top: 1px solid $border-lighter;
        padding-top: 10px;
        
        .stat-detail {
          display: flex;
          justify-content: space-between;
          color: $text-secondary;
          font-size: 13px;
          
          .el-tag {
            margin-right: 5px;
          }
        }
      }
    }
    
    .quick-actions {
      margin: 20px 0 30px;
      
      h2 {
        font-size: 18px;
        margin-bottom: 15px;
        color: $text-primary;
      }
      
      .action-card {
        height: 160px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.3s;
        
        &:hover {
          transform: translateY(-5px);
          box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        }
        
        .action-icon {
          width: 50px;
          height: 50px;
          border-radius: 50%;
          background-color: rgba($primary-color, 0.1);
          display: flex;
          justify-content: center;
          align-items: center;
          margin-bottom: 15px;
          
          .el-icon {
            font-size: 24px;
            color: $primary-color;
          }
        }
        
        .action-title {
          font-size: 16px;
          font-weight: bold;
          color: $text-primary;
          margin-bottom: 5px;
        }
        
        .action-desc {
          font-size: 13px;
          color: $text-secondary;
          text-align: center;
        }
      }
    }
    
    .recent-tasks {
      margin-top: 30px;
      
      .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
        
        h2 {
          font-size: 18px;
          color: $text-primary;
          margin: 0;
        }
      }
    }
  }
}
</style>