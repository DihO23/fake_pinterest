# criar as rotas do nosso site (os links)
from flask import render_template, url_for, redirect
from fakepinterest import app, database, bcrypt
from fakepinterest.models import Usuario, Foto
from flask_login import login_required, login_user, logout_user, current_user
from fakepinterest.forms import FormLogin, FormCriarConta, FormFoto
import os
from werkzeug.utils import secure_filename


@app.route("/", methods=["GET", "POST"])
def homepage():
  form_login = FormLogin()
  if form_login.validate_on_submit():
    usuario = Usuario.query.filter_by(email=form_login.email.data).first()
    if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
      login_user(usuario, remember=True)
      return redirect(url_for("perfil", id_usuario=usuario.id))
  return render_template("homepage.html", form=form_login)


@app.route("/criar-conta", methods=["GET", "POST"])
def criarconta():
    form_criarconta = FormCriarConta() 
    if form_criarconta.validate_on_submit():
        senha = bcrypt.generate_password_hash(form_criarconta.senha.data).decode("utf-8")
        usuario = Usuario(
            username=form_criarconta.username.data, 
            senha=senha,
            email=form_criarconta.email.data
        )
        database.session.add(usuario)
        database.session.commit()
        login_user(usuario, remember=True)
        return redirect(url_for("perfil", id_usuario=usuario.id))
    
    # Se o formulário não for validado, renderize o template de criação de conta
    return render_template("criarconta.html", form=form_criarconta)


@app.route("/perfil/<id_usuario>", methods=["GET", "POST"])
@login_required
def perfil(id_usuario):
  if int(id_usuario) == int(current_user.id):
    # O usuário está acessando o próprio perfil
    form_foto = FormFoto()
    if form_foto.validate_on_submit():
      arquivo = form_foto.foto.data
      nome_seguro = secure_filename(arquivo.filename)
      # Salvar a foto na pasta fotos_posts
      caminho = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        app.config["UPLOAD_FOLDER"],
        nome_seguro
      )
      arquivo.save(caminho)
      # Registra a foto no banco de dados
      foto = Foto(imagem=nome_seguro, id_usuario=current_user.id)
      database.session.add(foto)
      database.session.commit()
    return render_template("perfil.html", usuario=current_user, form=form_foto)
  else:
    usuario = Usuario.query.get(int(id_usuario))
    return render_template("perfil.html", usuario=usuario, form=None)


@app.route("/logout")
@login_required
def logout():
  login_user(current_user)
  return redirect(url_for("homepage"))


@app.route("/feed")
@login_required
def feed():
  fotos = Foto.query.order_by(Foto.data_criacao.desc()).all()
  return render_template("feed.html", fotos=fotos)