from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import create_app, db


app = create_app()
manager = Manager(app)

migrate = Migrate(app, db)  # 使用migrate绑定app和db

manager.add_command('db', MigrateCommand)  # 添加迁移脚本的命令


if __name__ == '__main__':
    manager.run()
