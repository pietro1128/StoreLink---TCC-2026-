from django.contrib.auth.tokens import PasswordResetTokenGenerator

class TokenRecuperacaoSenha(PasswordResetTokenGenerator):
    def _make_hash_value(self, usuario, timestamp):
        return f"{usuario.pk}{usuario.senha}{usuario.email}{timestamp}"
    
token_recuperacao = TokenRecuperacaoSenha()
    # O gerador nativo usa user.password e user.last_login, que o Usuario não tem.
    # Aqui definimos quais dados do Usuario entram no cálculo do token.
    # Como a senha entra nele, o token deixa de valer assim que a senha muda.
    