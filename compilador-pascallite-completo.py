"""
Compilador PascalLite - Implementación Completa
Fases: Análisis Léxico, Sintáctico, Semántico y Generación de Código MEPA

Autores: [Añadir nombres de los integrantes del grupo]
Fecha: [Añadir fecha]
"""

class Atomo:
    """Clase para representar los átomos (tokens) del lenguaje"""
    def __init__(self, tipo, lexema, linha, valor=None):
        self.tipo = tipo
        self.lexema = lexema
        self.linha = linha
        self.valor = valor

class TabelaSimbolos:
    """Gestiona la tabla de símbolos del compilador"""
    def __init__(self):
        self.tabela = {}
        self.proximo_endereco = 0
    
    def inserir(self, identificador, tipo):
        """Inserta una variable en la tabla de símbolos"""
        if identificador in self.tabela:
            raise Exception(f"Erro semântico: Variável '{identificador}' já foi declarada")
        self.tabela[identificador] = {
            'endereco': self.proximo_endereco,
            'tipo': tipo
        }
        self.proximo_endereco += 1
        return self.proximo_endereco - 1
    
    def buscar(self, identificador):
        """Busca una variable en la tabla de símbolos"""
        if identificador not in self.tabela:
            raise Exception(f"Erro semântico: Variável '{identificador}' não foi declarada")
        return self.tabela[identificador]['endereco']

class GeradorCodigo:
    """Gestiona la generación de código MEPA"""
    def __init__(self):
        self.proximo_rotulo = 1
        
    def novo_rotulo(self):
        """Genera un nuevo rótulo para el código MEPA"""
        rotulo = self.proximo_rotulo
        self.proximo_rotulo += 1
        return rotulo

class AnalizadorLexico:
    """Implementa el análisis léxico del compilador"""
    def __init__(self, codigo_fonte):
        self.codigo = codigo_fonte
        self.posicao = 0
        self.linha_atual = 1
        self.palavras_reservadas = {
            'program': 'PROGRAM', 'var': 'VAR', 'integer': 'INTEGER',
            'begin': 'BEGIN', 'end': 'END', 'if': 'IF',
            'then': 'THEN', 'else': 'ELSE', 'while': 'WHILE',
            'do': 'DO', 'read': 'READ', 'write': 'WRITE',
            'div': 'DIV', 'mod': 'MOD'
        }
    
    def proximo_char(self):
        """Obtiene el siguiente carácter del código fuente"""
        if self.posicao >= len(self.codigo):
            return None
        char = self.codigo[self.posicao]
        self.posicao += 1
        return char
    
    def peek_char(self):
        """Mira el siguiente carácter sin consumirlo"""
        if self.posicao >= len(self.codigo):
            return None
        return self.codigo[self.posicao]
    
    def voltar_char(self):
        """Retrocede una posición en el código fuente"""
        self.posicao -= 1
    
    def ignorar_espacos(self):
        """Ignora espacios en blanco y cuenta líneas"""
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
        """Lee y procesa comentarios"""
        c = self.proximo_char()
        if c == '*':  # Comentario de bloque (*...)
            while True:
                c = self.proximo_char()
                if c is None:
                    raise Exception(f"Erro léxico: comentário não fechado na linha {self.linha_atual}")
                if c == '\n':
                    self.linha_atual += 1
                elif c == '*' and self.peek_char() == ')':
                    self.proximo_char()
                    break
        elif c == '/':  # Comentario de línea //...
            while True:
                c = self.proximo_char()
                if c is None or c == '\n':
                    if c == '\n':
                        self.linha_atual += 1
                    break
    
    def ler_numero(self):
        """Lee y procesa números"""
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
        """Lee y procesa identificadores y palabras reservadas"""
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
            
        tipo = self.palavras_reservadas.get(ident.lower(), 'IDENTIF')
        return Atomo(tipo, ident, self.linha_atual)
    
    def obter_atomo(self):
        """Obtiene el siguiente átomo del código fuente"""
        self.ignorar_espacos()
        
        c = self.proximo_char()
        if c is None:
            return None
            
        # Procesar comentarios
        if c == '(' and self.peek_char() == '*':
            self.ler_comentario()
            return self.obter_atomo()
        elif c == '/' and self.peek_char() == '/':
            self.ler_comentario()
            return self.obter_atomo()
            
        # Procesar números
        if c.isdigit():
            self.voltar_char()
            return self.ler_numero()
            
        # Procesar identificadores y palabras reservadas
        if c.isalpha() or c == '_':
            self.voltar_char()
            return self.ler_identificador()
            
        # Procesar operadores y símbolos especiales
        if c == ':':
            if self.peek_char() == '=':
                self.proximo_char()
                return Atomo('ATRIB', ':=', self.linha_atual)
            return Atomo('DOIS_PONTOS', ':', self.linha_atual)
        
        if c == '<':
            if self.peek_char() == '=':
                self.proximo_char()
                return Atomo('MENOR_IGUAL', '<=', self.linha_atual)
            elif self.peek_char() == '>':
                self.proximo_char()
                return Atomo('DIFERENTE', '<>', self.linha_atual)
            return Atomo('MENOR', '<', self.linha_atual)
            
        if c == '>':
            if self.peek_char() == '=':
                self.proximo_char()
                return Atomo('MAIOR_IGUAL', '>=', self.linha_atual)
            return Atomo('MAIOR', '>', self.linha_atual)
            
        # Símbolos simples
        simbolos = {
            ';': 'PONTO_VIRG',
            ',': 'VIRGULA',
            '.': 'PONTO',
            '+': 'MAIS',
            '-': 'MENOS',
            '*': 'MULT',
            '/': 'DIV',
            '(': 'ABRE_PAR',
            ')': 'FECHA_PAR',
            '=': 'IGUAL'
        }
        
        if c in simbolos:
            return Atomo(simbolos[c], c, self.linha_atual)
            
        raise Exception(f"Erro léxico: caractere inválido '{c}' na linha {self.linha_atual}")

class Compilador:
    """Clase principal que implementa el compilador completo"""
    def __init__(self, codigo_fonte):
        self.lexico = AnalizadorLexico(codigo_fonte)
        self.tabela_simbolos = TabelaSimbolos()
        self.gerador = GeradorCodigo()
        self.lookahead = None
        self.linha_atual = 1
        
    def erro(self, mensagem):
        """Reporta un error y termina la compilación"""
        raise Exception(f"Erro na linha {self.linha_atual}: {mensagem}")
    
    def avancar(self):
        """Avanza al siguiente átomo"""
        self.lookahead = self.lexico.obter_atomo()
        if self.lookahead:
            print(f"Linha: {self.lookahead.linha} - atomo: {self.lookahead.tipo} lexema: {self.lookahead.lexema}")
    
    def consome(self, tipo):
        """Consume un átomo del tipo esperado"""
        if self.lookahead and self.lookahead.tipo == tipo:
            token = self.lookahead
            self.avancar()
            return token
        else:
            esperado = tipo
            encontrado = self.lookahead.tipo if self.lookahead else "EOF"
            self.erro(f"Esperado [{esperado}] encontrado [{encontrado}]")
    
    def programa(self):
        """Procesa la estructura principal del programa"""
        print("INPP")
        
        self.consome('PROGRAM')
        self.consome('IDENTIF')
        
        if self.lookahead and self.lookahead.tipo == 'ABRE_PAR':
            self.consome('ABRE_PAR')
            self.lista_identificadores()
            self.consome('FECHA_PAR')
        
        self.consome('PONTO_VIRG')
        self.bloco()
        self.consome('PONTO')
        
        print("PARA")
    
    def bloco(self):
        """Procesa un bloque de código"""
        if self.lookahead and self.lookahead.tipo == 'VAR':
            self.declaracoes_variaveis()
        self.comando_composto()
    
    def declaracoes_variaveis(self):
        """Procesa las declaraciones de variables"""
        self.consome('VAR')
        num_vars = self.declaracao()
        
        while self.lookahead and self.lookahead.tipo == 'PONTO_VIRG':
            self.consome('PONTO_VIRG')
            if self.lookahead and self.lookahead.tipo != 'BEGIN':
                num_vars += self.declaracao()
        
        self.consome('PONTO_VIRG')
        print(f"AMEM {num_vars}")
    
    def declaracao(self):
        """Procesa una declaración de variables"""
        ids = []
        ids.append(self.consome('IDENTIF').lexema)
        
        while self.lookahead and self.lookahead.tipo == 'VIRGULA':
            self.consome('VIRGULA')
            ids.append(self.consome('IDENTIF').lexema)
        
        self.consome('DOIS_PONTOS')
        tipo = self.tipo()
        
        for id in ids:
            self.tabela_simbolos.inserir(id, tipo)
        
        return len(ids)
    
    def tipo(self):
        """Procesa el tipo de una variable"""
        if self.lookahead.tipo == 'INTEGER':
            self.consome('INTEGER')
            return 'INTEGER'
        self.erro("Tipo de variável inválido")
    
    def comando_composto(self):
        """Procesa un comando compuesto (begin...end)"""
        self.consome('BEGIN')
        self.comando()
        
        while self.lookahead and self.lookahead.tipo == 'PONTO_VIRG':
            self.consome('PONTO_VIRG')
            if self.lookahead and self.lookahead.tipo != 'END':
                self.comando()
        
        self.consome('END')
    
    def comando(self):
        """Procesa un comando"""
        if not self.lookahead:
            self.erro("Comando esperado")
            
        if self.lookahead.tipo == 'IDENTIF':
            self.comando_atribuicao()
        elif self.lookahead.tipo == 'IF':
            self.comando_if()
        elif self.lookahead.tipo == 'WHILE':
            self.comando_while()
        elif self.lookahead.tipo == 'READ':
            self.comando_entrada()
        elif self.lookahead.tipo == 'WRITE':
            self.comando_saida()
        elif self.lookahead.tipo == 'BEGIN':
            self.comando_composto()
        else:
            self.erro("Comando inválido")
    
    def comando_atribuicao(self):
        """Procesa un comando de atribución"""
        id_token = self.consome('IDENTIF')
        endereco = self.tabela_simbolos.buscar(id_token.lexema)
        self.consome('ATRIB')
        self.expressao()
        print(f"ARMZ {endereco}")
    
    def comando_if(self):
        """Procesa un comando if"""
        self.consome('IF')
        self.expressao()
        L1 = self.gerador.novo_rotulo()
        print(f"DSVF L{L1}")
        self.consome('THEN')
        self.comando()
        
        if self.lookahead and self.lookahead.tipo == 'ELSE':
            L2 = self.gerador.novo_rotulo()
            print(f"DSVS L{L2}")
            print(f"L{L1}: NADA")
            self.consome('ELSE')
            self.comando()
            print(f"L{L2}: NADA")
        else:
            print(f"L{L1}: NADA")
    
    def comando_while(self):
        """Procesa un comando while"""
        L1 = self.gerador.novo_rotulo()
        L2 = self.gerador.novo_rotulo()
        
        self.consome('WHILE')
        print(f"L{L1}: NADA")
        self.expressao()
        print(f"DSVF L{L2}")
        self.consome('DO')
        self.comando()
        print(f"DSVS L{L1}")
        print(f"L{L2}: NADA")
    
    def comando_entrada(self):
        """Procesa un comando de entrada (read)"""
        self.consome
