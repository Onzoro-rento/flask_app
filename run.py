from app import create_app

app = create_app()
import os
# print("template_folder:", os.path.abspath(app.template_folder))
# print("login_form.html exists:", os.path.exists("templates/login_form.html"))

# print("テンプレート一覧:")
# for root, dirs, files in os.walk(app.template_folder):
#     for file in files:
#         print(" -", os.path.join(root, file))

# print("実行中のファイル:", __file__)
# print("Jinja2 template search paths:")
# for path in app.jinja_loader.searchpath:
#     print(" -", path)

if __name__ == '__main__':
    app.run(debug=True)



