## EiBlog

What is EiBlog?

**基于flask框架的、使用python语言编写的有完整功能的Blog**

目前完成的功能：
1.博客主页面  2.博客编写  3.博客修改/删除 4.文章分类查看 5.登陆注册
6.评论功能    7.管理员页面

后期计划将一部分代码转至前端，改进一下标签功能。


使用方法：
1.Clone至本地，创建一个新的虚拟环境，按requirements.txt安装所需的包；
2.在Eiblog目录下创建config.py，按config.template和自己的数据库设置填写。
3.创建一个名为Eiblog的charset=utf8mb4的数据库。
4.在命令行下切换至Eiblog目录，依次运行python manage.py db init python manage.py db migrate
python manage.py db ungrade
5.python manage.py runserver
6.打开localhost:5000即可

·要获得管理员权限需要进入数据库将该用户的admin值改为1