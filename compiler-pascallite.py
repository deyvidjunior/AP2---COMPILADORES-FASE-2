# Implementación del Compilador PascalLite
# Análisis Léxico y Sintáctico

class Atomo:
    def __init__(self, tipo, lexema, linha, valor=None):
        self.tipo = tipo
        self.lexema = lexema
        self.linha = linha
        self.valor = valor

class AnalizadorLexico:
    def __init__(self, codigo_fonte):
        self.codigo = codigo_fonte
        self.posicao = 0
        self.linha_atual = 1
        self.palavras_reservadas = {
            'begin': 'BEGIN', 'boolean': 'BOOLEAN', 'div': 'DIV',
            'do': 'DO', 'else': 'ELSE', 'end': 'END',
            'false': 'FALSE', 'if': 'IF', 'integer': 'INTEGER',
            'mod': 'MOD', 'program': 'PROGRAM', 'read': 'READ',
            'then': 'THEN', 'true': 'TRUE', 'not': 'NOT',
            'var': 'VAR', 'while': 'WHILE', 'write': 'WRITE'
        }
    
    def proximo_char(self):
        if self.posicao >= len(self.codigo):
            return None
        char = self.codigo[self.posicao]
        self.posicao += 1
        return char
    
    def peek_char(self):
        if self.posicao >= len(self.codigo):
            return None
        return self.codigo[self.posicao]

    def voltar_char(self):
        self.posicao -= 1
    
    def ignorar_espacos(self):
        while True:
            c = self.proximo_char()
            if c is None:
                return None
            if c == '\n':
                self.linha_atual += 1
            elif c not in [' ', '\t', '\r']:
                self.voltar_char()
                break
    
    def ler_comentario(self):
        c = self.proximo_char()
        if c == '/':  # Comentário de linha
            while True:
                c = self.proximo_char()
                if c is None or c == '\n':
                    if c == '\n':
                        self.linha_atual += 1
                    break
        elif c == '*':  # Comentário de bloco
            while True:
                c = self.proximo_char()
                if c is None:
                    raise Exception(f"Erro léxico: comentário não fechado na linha {self.linha_atual}")
                if c == '\n':
                    self.linha_atual += 1
                elif c == '*' and self.peek_char() == ')':
                    self.proximo_char()  # Consumir o ')'
                    break
    
    def ler_numero(self):
        numero = ""
        while True:
            c = self.proximo_char()
            if c is None or not c.isdigit():
                if c is not None:
                    self.voltar_char()
                break
            numero += c
        return Atomo('NUM', numero, self.linha_atual, int(numero))
    
    def ler_identificador(self):
        ident = ""
        while True:
            c = self.proximo_char()
            if c is None or (not c.isalnum() and c != '_'):
                if c is not None:
                    self.voltar_char()
                break
            ident += c
            
        if len(ident) > 20:
            raise Exception(f"Erro léxico: identificador muito longo na linha {self.linha_atual}")
            
        # Verificar se é palavra reservada
        tipo = self.palavras_reservadas.get(ident.lower(), 'IDENTIF')
        return Atomo(tipo, ident, self.linha_atual)
    
    def obter_atomo(self):
        self.ignorar_espacos()
        
        c = self.proximo_char()
        if c is None:
            return None
            
        # Comentários
        if c == '(' and self.peek_char() == '*':
            self.ler_comentario()
            return self.obter_atomo()
            
        # Números
        if c.isdigit():
            self.voltar_char()
            return self.ler_numero()
            
        # Identificadores e palavras reservadas
        if c.isalpha() or c == '_':
            self.voltar_char()
            return self.ler_identificador()
            
        # Operadores e símbolos especiais
        if c == ':':
            if self.peek_char() == '=':
                self.proximo_char()
                return Atomo('ATRIB', ':=', self.linha_atual)
            return Atomo('DOIS_PONTOS', ':', self.linha_atual)
            
        # Outros símbolos simples
        simbolos = {
            ';': 'PONTO_VIRG',
            ',': 'VIRGULA',
            '.': 'PONTO',
            '+': 'MAIS',
            '-': 'MENOS',
            '*': 'VEZES',
            '/': 'DIV',
            '(': 'ABRE_PAR',
            ')': 'FECHA_PAR'
        }
        
        if c in simbolos:
            return Atomo(simbolos[c], c, self.linha_atual)
            
        raise Exception(f"Erro léxico: caractere inválido '{c}' na linha {self.linha_atual}")

class AnalizadorSintatico:
    def __init__(self, codigo_fonte):
        self.lexico = AnalizadorLexico(codigo_fonte)
        self.lookahead = None
        self.linha_atual = 1
        self.avancar()
    
    def avancar(self):
        self.lookahead = self.lexico.obter_atomo()
        if self.lookahead:
            print(f"Linha: {self.lookahead.linha} - atomo: {self.lookahead.tipo} lexema: {self.lookahead.lexema}")
    
    def consome(self, tipo):
        if self.lookahead and self.lookahead.tipo == tipo:
            self.avancar()
        else:
            esperado = tipo
            encontrado = self.lookahead.tipo if self.lookahead else "EOF"
            raise Exception(f"Erro sintático: Esperado [{esperado}] encontrado [{encontrado}] na linha {self.linha_atual}")
    
    def programa(self):
        self.consome('PROGRAM')
        self.consome('IDENTIF')
        if self.lookahead and self.lookahead.tipo == 'ABRE_PAR':
            self.consome('ABRE_PAR')
            self.lista_identificadores()
            self.consome('FECHA_PAR')
        self.consome('PONTO_VIRG')
        self.bloco()
        self.consome('PONTO')

def main():
    # Ejemplo de uso
    codigo = """
    program exemplo1;
    var num: integer;
    begin
        num := 10;
        write(num)
    end.
    """
    
    try:
        compilador = AnalizadorSintatico(codigo)
        compilador.programa()
        print(f"{compilador.linha_atual} linhas analisadas, programa sintaticamente correto.")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
