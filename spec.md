## 开发文档(一期)

供个人使用的博客系统，不提供第三方注册。

### 技术选型

> - python 3.6
> - mysql 5.7
> - flask 1.0
> - sqlalchemy(flask-sqlalchemy)

### 需求

删除的功能在二期实现

> - 首页（文章列表）
> - 文章页面
> - ~~文章评论~~
> - 分类页面
> - ~~标签页面~~
> - ~~用户注册~~
> - 用户登陆
> - ~~用户管理~~
> - 文章管理(增删改查)
> - ~~评论管理~~
> - 分类管理

### 数据库设计

User
列名 | 类型 | 描述
 - | - | - 
id| int |
email | string |
username | string |
password | string |
is_admin | boolean | 

Article
列名 | 类型 | 描述
 - | - | - 
 id| int |
user_id | int | 不使用外键，强关联不易维护
category_id | string | 
tags | string |
title| string | 
content | text |
created_at | datetime | 

Category
列名 | 类型 | 描述
 - | - | - 
id| int |
name | string| 
