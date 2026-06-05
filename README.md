# 奶茶店原料开封效期与报损管理系统

基于前后端分离架构的奶茶店原料管理系统，实现原料全生命周期管理。

## 技术栈

### 后端
- **Python** - 编程语言
- **Litestar** - Web 框架
- **SQLAlchemy** - ORM 框架
- **PostgreSQL** - 数据库
- **JWT** - 身份认证

### 前端
- **Vue 3** - 前端框架
- **TypeScript** - 类型系统
- **Naive UI** - UI 组件库
- **Pinia** - 状态管理
- **Vue Router** - 路由管理
- **ECharts** - 数据可视化

## 核心功能

### 1. 登录认证
- JWT Token 认证
- 管理员/普通用户权限区分

### 2. 门店管理
- 门店信息增删改查

### 3. 原料分类
- 原料分类管理

### 4. 原料档案
- 原料编号、名称、规格、分类、保质期等信息管理
- 原料编号唯一性校验
- 支持按名称、分类、状态筛选查询

### 5. 入库登记
- 原料入库记录
- 自动更新库存数量
- 记录批号、供应商、采购日期、失效日期

### 6. 开封登记
- 原料开封记录
- 失效日期不能早于开封日期校验
- 已失效原料不能继续开封
- 同一原料同一天不能重复开封

### 7. 报损登记
- 原料报损记录
- 报损数量不能超过当前库存校验
- 记录报损原因

### 8. 效期预警
- 临期原料提醒
- 已过期原料预警

### 9. 数据看板
- 临期/过期原料数量统计
- 报损排行榜
- 分类库存分布图（饼图）

## 业务约束

- ✅ 原料编号不能重复
- ✅ 报损数量不能超过当前库存
- ✅ 失效日期不能早于开封日期
- ✅ 已失效原料不能继续开封
- ✅ 同一原料同一天不能重复录入开封记录

## 快速开始

### 前置要求
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+

### 数据库准备

```sql
CREATE DATABASE milk_tea_shop;
```

### 后端启动

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 复制环境变量配置
cp .env.example .env
# 修改 .env 中的数据库连接信息

# 初始化数据库（创建表和默认数据）
python init_db.py

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端 API 文档地址: http://localhost:8000/docs

### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务
npm run dev
```

前端访问地址: http://localhost:3000

## 默认账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 管理员 |
| user | user123 | 普通用户 |

## 项目结构

```
cj64/
├── backend/                 # 后端项目
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py         # 应用入口
│   │   ├── config.py       # 配置文件
│   │   ├── database.py     # 数据库连接
│   │   ├── models.py       # 数据模型
│   │   ├── schemas.py      # Pydantic 模式
│   │   ├── security.py     # 安全认证
│   │   ├── dependencies.py # 依赖注入
│   │   └── routers/        # API 路由
│   │       ├── auth.py
│   │       ├── stores.py
│   │       ├── categories.py
│   │       ├── materials.py
│   │       ├── stock_ins.py
│   │       ├── open_records.py
│   │       ├── damage_records.py
│   │       └── dashboard.py
│   ├── init_db.py          # 数据库初始化脚本
│   ├── requirements.txt
│   └── .env.example
└── frontend/               # 前端项目
    ├── src/
    │   ├── main.ts
    │   ├── App.vue
    │   ├── style.css
    │   ├── router/         # 路由配置
    │   ├── stores/         # Pinia 状态管理
    │   ├── utils/          # 工具函数
    │   ├── layouts/        # 布局组件
    │   └── views/          # 页面组件
    ├── index.html
    ├── package.json
    ├── tsconfig.json
    └── vite.config.ts
```

## API 接口

### 认证
- `POST /auth/login` - 登录
- `GET /auth/me` - 获取当前用户信息

### 门店
- `GET /stores` - 获取门店列表
- `POST /stores` - 新增门店
- `PUT /stores/{id}` - 更新门店
- `DELETE /stores/{id}` - 删除门店

### 原料分类
- `GET /categories` - 获取分类列表
- `POST /categories` - 新增分类
- `PUT /categories/{id}` - 更新分类
- `DELETE /categories/{id}` - 删除分类

### 原料档案
- `GET /materials` - 获取原料列表（支持筛选）
- `POST /materials` - 新增原料
- `PUT /materials/{id}` - 更新原料
- `DELETE /materials/{id}` - 删除原料

### 入库登记
- `GET /stock-ins` - 获取入库记录
- `POST /stock-ins` - 新增入库
- `DELETE /stock-ins/{id}` - 删除入库记录

### 开封登记
- `GET /open-records` - 获取开封记录
- `POST /open-records` - 新增开封
- `DELETE /open-records/{id}` - 删除开封记录

### 报损登记
- `GET /damage-records` - 获取报损记录
- `POST /damage-records` - 新增报损
- `DELETE /damage-records/{id}` - 删除报损记录

### 看板统计
- `GET /dashboard/stats` - 获取看板统计数据
- `GET /dashboard/expiry-warnings` - 获取效期预警列表
