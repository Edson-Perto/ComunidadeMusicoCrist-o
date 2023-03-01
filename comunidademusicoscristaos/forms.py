from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from comunidademusicoscristaos.models import Usuario
from flask_login import current_user


class FormCriarConta(FlaskForm):
    usuario = StringField('Nome de usuário', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(6, 20)])
    confirmacao_senha = PasswordField('Confirme a senha', validators=[DataRequired(), EqualTo('senha')])
    igreja = StringField('Igreja/Cominudade', validators=[DataRequired()])
    botao_submit_criarconta = SubmitField('Criar conta')

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError('E-mail já cadastrado. Tente outro.')


class FormLogin(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(6, 20)])
    lembrar_dados = BooleanField('Lembrar dados de acesso')
    botao_submit_login = SubmitField('Entrar')


class FormEditarPerfil(FlaskForm):
    usuario = StringField('Nome de usuário', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    foto_perfil = FileField('Atualizar imagem', validators=[FileAllowed(['jpg', 'png'])])
    botao_submit_editarperfil = SubmitField('Confirmar Edição')
    instrum_violao = BooleanField('Violão')
    instrum_guitarra = BooleanField('Gutarra')
    instrum_baixo = BooleanField('Baixo')
    instrum_bateria = BooleanField('Bateria')
    instrum_teclado = BooleanField('Teclado')
    instrum_outros = BooleanField('Marque para adcionar outros: (Separe os instrumentos com vírgula)')
    outros = StringField()

    def validate_email(self, email):
        if current_user.email != email.data:
            usuario = Usuario.query.filter_by(email=email.data).first()
            if usuario:
                raise ValidationError('Já existe um um usuárui com este i-mail. Tente outro.')


class FormCriarPost(FlaskForm):
    titulo = StringField('Título do post:', validators=[DataRequired(), Length(2, 130)])
    corpo = TextAreaField('Escreva aqui.', validators={DataRequired()})
    botao_submit = SubmitField('Postar')