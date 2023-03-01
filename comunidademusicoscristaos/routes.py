from flask import render_template, redirect, url_for, flash, request, abort
from comunidademusicoscristaos import app, database, bcrypt
from comunidademusicoscristaos.forms import FormCriarConta, FormLogin, FormEditarPerfil, FormCriarPost
from comunidademusicoscristaos.models import Usuario, Post
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
from PIL import Image  #PLI é a biblioteca Pillow


@app.route("/")
def home():
    posts = Post.query.order_by(Post.id.desc())
    return render_template('home.html', posts=posts)


@app.route("/contato")
def contato():
    return render_template('contato.html')


@app.route('/usuarios')
@login_required
def usuarios():
    lista_usuarios = Usuario.query.all()
    return render_template('usuarios.html', lista_usuarios=lista_usuarios)


@app.route('/login', methods=['GET', 'POST'])  # isto deve ser passado para toda página q contnha um formulário
def login():
    form_login = FormLogin()
    form_criarconta = FormCriarConta()

    if form_login.validate_on_submit() and 'botao_submit_login' in request.form:
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario, remember=form_login.lembrar_dados.data)
            flash(f'Login executado com sucesso. "{form_login.email.data}" entrou.', 'alert-success')
            par_next = request.args.get('next')
            if par_next:
                return redirect(par_next)
            else:
                return redirect(url_for('home'))
        else:
            flash(f'E-mail ou Senha Incorretos.', 'alert-danger')
    if form_criarconta.validate_on_submit() and 'botao_submit_criarconta' in request.form:
        senha_cript = bcrypt.generate_password_hash(form_criarconta.senha.data)
        # criou o usuário - nome email senha
        usuario = Usuario(nome_usuario=form_criarconta.usuario.data, email=form_criarconta.email.data, senha=senha_cript, igreja=form_criarconta.igreja.data)
        # adcionar a sessão
        database.session.add(usuario)
        # commit na sessão
        database.session.commit()
        flash(f'Conta criada com sucesso para "{form_criarconta.email.data}"', 'alert-success')
        return redirect(url_for('login'))
    return render_template('login.html', form_login=form_login, form_criarconta=form_criarconta)


@app.route('/sair')
@login_required
def sair():
    email_logado = current_user.email
    logout_user()
    flash(f'"{email_logado}" saiu.', 'alert-success')
    return redirect(url_for('home'))


@app.route('/perfil')
@login_required
def perfil():
    foto_perfil = url_for('static', filename=f'fotos_perfil/{current_user.foto_perfil}')
    return render_template('perfil.html', foto_perfil=foto_perfil)


@app.route('/post/criar', methods=['GET', 'POST'])
@login_required
def criar_post():
    form = FormCriarPost()
    if form.validate_on_submit():
        post = Post(titulo=form.titulo.data, corpo=form.corpo.data, autor=current_user)
        database.session.add(post)
        database.session.commit()
        flash('Post criado com sucesso', 'alert-success')
        return redirect(url_for('home'))
    return render_template('criarpost.html', form=form)


def salvar_imagem(imagem):
    # adicionando um código ao nome da imgem
    codigo = secrets.token_hex(8)
    nome, extençao = os.path.splitext(imagem.filename)
    nome_arquivo = nome + codigo + extençao
    caminho_completo = os.path.join(app.root_path, 'static/fotos_perfil', nome_arquivo)

    # redizindo o tamanho da imagem
    tamanho = (200, 200)
    imagem_reduzida = Image.open(imagem)
    imagem_reduzida.thumbnail(tamanho)

    # salvando a imagemna parta fotos_perfil
    imagem_reduzida.save(caminho_completo)
    return nome_arquivo


def atualizar_instrum(form):
    lista_instrumentos = []
    outros = form.outros
    for campo in form:
        if 'instrum_' in campo.name:
            if campo.data:
                if '_outros' in campo.name:
                    outros = outros.data.replace(', ', ';').replace(',', ';')
                    lista_instrumentos.append(outros)
                else:
                    lista_instrumentos.append(campo.label.text)


    return ';'.join(lista_instrumentos)


@app.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    form = FormEditarPerfil()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.nome_usuario = form.usuario.data
        #current_user.
        if form.foto_perfil.data:
            nome_imagem = salvar_imagem(form.foto_perfil.data)
            current_user.foto_perfil = nome_imagem
        current_user.instrumentos = atualizar_instrum(form)
        database.session.commit()
        flash('Perfil editado com sucesso.', 'alert-success')
        return redirect(url_for('perfil'))
    elif request.method == "GET":
        form.email.data = current_user.email
        form.usuario.data = current_user.nome_usuario
    foto_perfil = url_for('static', filename=f'fotos_perfil/{current_user.foto_perfil}')
    return render_template('editarperfil.html', foto_perfil=foto_perfil, form=form)


@app.route('/post/<post_id>', methods=['GET', 'POST'])
@login_required
def exibir_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        form = FormCriarPost()
        if request.method == "GET":
            form.titulo.data = post.titulo
            form.corpo.data = post.corpo
        elif form.validate_on_submit():
            post.titulo = form.titulo.data
            post.corpo = form.corpo.data
            database.session.commit()
            flash('Post atualizado com sucesso', 'alert-success')
    else:
        form = None
    return render_template('post.html', post=post, form=form)


@app.route('/post/<post_id>/excluir', methods=['GET', 'POST'])
@login_required
def excluir_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        database.session.delete(post)
        database.session.commit()
        flash('Post excluido com sucesso!', 'alert-danger')
        return redirect(url_for('home'))
    else:
        abort(403)

