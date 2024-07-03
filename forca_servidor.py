import socket


HOST = '10.93.2.230'
PORT = 55555

class Jogador:
    def __init__(self, soc, adr, n) -> None:
        self.soc = soc
        self.adr = adr
        self.pontos = 0
        self.numero = n
        self.vidas = 6

    def enviar_mensagem(self, msg):
        tamanho = len(msg)
        self.soc.send(f'{tamanho:02}{msg}'.encode('ascii'))

    def receber_mensagem(self):
        tamanho = self.soc.recv(2).decode('ascii')
        try:
            mensagem = self.soc.recv(int(tamanho)).decode('ascii')
            return mensagem
        except:
            exit()


class Game:
    def __init__(self) -> None:
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((HOST, PORT))
        self.server.listen(0)
        self.numero_jogadores = 0
        self.lista_de_jogadores = []
        self.rodada = 0
        self.vez = 0
        self.segredo = ''
        self.segredo_oculto = ''
        self.ganhador = None
        self.letras_pedidas = []
        self.log = []

    def adicionar_jogador(self, jogador):
        self.lista_de_jogadores.append(jogador)
        self.numero_jogadores += 1
        mensagem = f'/i{self.numero_jogadores}'
        jogador.enviar_mensagem(mensagem)

    def pedir_palavra(self):
        mensagem = '/palavra'
        indice_jogador = self.rodada%self.numero_jogadores
        self.lista_de_jogadores[indice_jogador].enviar_mensagem(mensagem)
        palavra = self.lista_de_jogadores[indice_jogador].receber_mensagem()
        self.segredo = palavra
        for i in range(len(palavra)):
            self.segredo_oculto += '*' if self.segredo[i] != ' ' else ' '

    def pedir_letra(self):
        while True:
            mensagem = f'/letra{self.segredo_oculto}'
            jogador = self.lista_de_jogadores[self.vez]
            jogador.enviar_mensagem(mensagem)
            letra = jogador.receber_mensagem()
            if letra not in self.letras_pedidas:
                break
            mensagem = f'A letra {letra} ja foi, tente outra'
            jogador.enviar_mensagem(mensagem)
        self.letras_pedidas.append(letra)
        return letra

    def atualizar_segredo(self):
        letra_pedida = self.letras_pedidas[-1]
        estado_atual = self.segredo_oculto
        self.segredo_oculto = ''
        for i in range(len(estado_atual)):
            if estado_atual[i] != '*':
                self.segredo_oculto += estado_atual[i]
            elif self.segredo[i] == letra_pedida:
                self.segredo_oculto += self.segredo[i]
            elif self.segredo[i] == ' ':
                self.segredo_oculto += ' '
            else:
                self.segredo_oculto += '*'
        
    def enviar_estado(self):
        estado = '/e'
        for jogador in self.lista_de_jogadores:
            estado += f'{jogador.numero}{jogador.vidas}{jogador.pontos:02}'
        self.broadcast(estado)

    def processar_rodada(self):
        self.pedir_palavra()
        if self.segredo == '/q':
            self.broadcast('/resultado')
            self.sair()
        
        self.broadcast(f'/s{self.segredo_oculto}')


        while True:
            if self.vez == self.rodada:
                self.vez = (self.vez+1)%self.numero_jogadores

            soma = 0

            for i in range(len(self.lista_de_jogadores)):
                if i == self.rodada:
                    continue
                soma += self.lista_de_jogadores[i].vidas
            
            # print('soma')
            # print(soma)
            if soma == 0:
                self.broadcast("Os jogadores morreram e a rodada acabou.")
                break

            jogador = self.lista_de_jogadores[self.vez]

            if jogador.vidas == 0:
                self.vez = (self.vez+1)%self.numero_jogadores
                continue                

            letra = self.pedir_letra()

            if letra not in self.segredo:
                jogador.vidas -= 1
                print('rodada:')
                print(self.rodada)
                dono = self.lista_de_jogadores[self.rodada]
                dono.pontos += 1
                self.broadcast(f'A letra {letra} nao esta na palvra. O jogador {self.vez+1} perdeu uma vida.')
                if jogador.vidas == 0:
                    self.broadcast(f'O jogador {self.vez+1} morreu')
                    # break
                self.vez = (self.vez+1)%self.numero_jogadores
            else:
                for l in self.segredo:
                    jogador.pontos += 1 if l == letra else 0

                self.broadcast(f'A letra {letra} esta na palavra. O jogador {self.vez+1} continua.')
                self.atualizar_segredo()


            self.broadcast(f'/s{self.segredo_oculto}')

            if self.segredo == self.segredo_oculto:
                # jogador da vez ganhou a rodada
                self.broadcast(f"O jogador {self.vez+1} acertou a palavra e ganhou a rodada.")
                break

            self.enviar_estado()

            print(self.segredo)
            print(self.segredo_oculto)

    def receber_conexao(self):
        while self.numero_jogadores < 3:
            soc, adr = self.server.accept()
            print(f'Cliente conectado: {str(adr)}')
            jogador = Jogador(soc, adr, self.numero_jogadores+1)
            self.adicionar_jogador(jogador)

    def broadcast(self, msg):
        for jogador in self.lista_de_jogadores:
            try:
                jogador.enviar_mensagem(msg)
            except:
                exit()

    def reiniciar_variaveis(self):
        self.rodada += 1
        self.segredo = ''
        self.segredo_oculto = ''
        self.letras_pedidas = []
        self.vez = 0
        for jogador in self.lista_de_jogadores:
            jogador.vidas = 6

    def jogar(self):
        while self.ganhador == None:
            self.enviar_estado()
            self.processar_rodada()
            self.reiniciar_variaveis()
            if self.rodada == 3:
                self.broadcast('/resultado')
                break
            
    def sair(self):
        input('>>')
        try:
            self.broadcast('/q')
            self.server.shutdown(socket.SHUT_RDWR)
            self.server.close()
        finally:
            exit()

jogo = Game()

jogo.receber_conexao()

jogo.jogar()

jogo.sair()
