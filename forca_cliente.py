import socket
import pygame
from pygame.locals import *
import threading

HOST = '10.93.2.230'
PORT = 55555
WIDTH = 960
HEIGHT = 540

class Game:
    def __init__(self) -> None:
        self.conexao = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conexao.connect((HOST, PORT))
        self.numero = None
        self.forcar_parada = False

        self.pedir_palavra = False
        self.pedir_letra = False
        self.segredo = ''
        self.buffer = ''
        self.buffer_aux = ''

        self.log = []
        self.jogadores = []

        self.finalizar = False
        
        #   graficos
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Jogo da forca")
        self.clock = pygame.time.Clock()
        self.fonte1 = pygame.font.SysFont('monospace', 40)
        self.fonte2 = pygame.font.SysFont('monospace', 26)
        self.fonte3 = pygame.font.SysFont('monospace', 20)
        self.main_rect = pygame.Rect(WIDTH*0.25, 0, WIDTH*0.75, HEIGHT*5/9)
        self.log_rect = pygame.Rect(WIDTH*0.25, HEIGHT*5/9, WIDTH*0.75, HEIGHT*4/9)
        self.players_rect = pygame.Rect(0, 0, WIDTH*0.25, HEIGHT)
        self.type_rect = pygame.Rect(WIDTH*0.25, HEIGHT*5/9-50, WIDTH*0.75, 50)

    def enviar_mensagem(self, msg):
        tamanho = len(msg)
        self.conexao.send(f'{tamanho:02}{msg}'.encode('ascii'))

    def receber_datagrama(self):
        tamanho = self.conexao.recv(2).decode('ascii')

        try:
            t = int(tamanho)
        except:
            raise Exception("Conexao encerrada")

        mensagem = self.conexao.recv(int(tamanho)).decode('ascii')

        if mensagem.startswith('/q'):
            self.conexao.close()
            self.forcar_parada = True

        elif mensagem.startswith('/palavra'):
            self.pedir_palavra = True
            print("Escolha uma palavra:")
            # palavra = input('>>')
            while self.buffer == '':
                if self.forcar_parada:
                    break    
                
            self.enviar_mensagem(self.buffer)
            self.pedir_palavra = False
            self.buffer = ''

        elif mensagem.startswith('/i'):
            self.numero = int(mensagem[2])
            print(f'voce e o jogador {self.numero}')

        elif mensagem.startswith('/letra'):
            print(mensagem[6:])
            self.segredo = mensagem[6:]
            self.pedir_letra = True
            print('Escolha uma letra:')
            while len(self.buffer) != 1:
                pass
            self.enviar_mensagem(self.buffer)
            self.pedir_letra = False
            self.buffer = ''

        elif mensagem.startswith('/s'):
            self.segredo = mensagem[2:]
        
        elif mensagem.startswith('/e'):
            print(mensagem)
            n_jogadores = int((int(tamanho)-2)/4)
            for i in range(n_jogadores): 
                numero = int(mensagem[2+4*i])-1
                vidas = int(mensagem[3+4*i])
                pontos = int(mensagem[4+4*i:6+4*i])
                jogador = {'vidas': vidas, 'pontos': pontos}
                if numero < len(self.jogadores):
                    self.jogadores[numero] = jogador
                else:
                    self.jogadores.append(jogador)

        elif mensagem.startswith('/resultado'):
            self.finalizar = True

        else:
            print(mensagem)
            self.log.append(mensagem)

    def loop_receber(self):
        while True:
            try:
                self.receber_datagrama()
            except Exception as erro:
                # print('houve um erro')
                # print(erro)
                break

    def desenhar_tela(self):
        pygame.draw.rect(self.screen, 'black', self.main_rect)
        pygame.draw.rect(self.screen, 'black', self.players_rect)
        pygame.draw.rect(self.screen, 'black', self.log_rect)
        pygame.draw.line(self.screen, 'white', (0.25*WIDTH, 0), (0.25*WIDTH, HEIGHT))
        pygame.draw.line(self.screen, 'white', (0.25*WIDTH, HEIGHT*5/9), (WIDTH, HEIGHT*5/9))
        pygame.draw.line(self.screen, 'white', (0.25*WIDTH, HEIGHT*5/9-50), (WIDTH, HEIGHT*5/9-50))
        segredo_surf = self.fonte1.render(self.segredo, True, 'white')
        dimensoes = self.fonte1.size(self.segredo)
        self.screen.blit(segredo_surf, (0.25*WIDTH+0.75*WIDTH/2-dimensoes[0]/2, HEIGHT*5/9/2-dimensoes[1]))
        

        for i in range(min(8, len(self.log))):
            msg = self.log[-i-1]
            texto_surf = self.fonte3.render(msg, True, 'white')
            self.screen.blit(texto_surf, (self.log_rect.x+10, self.log_rect.y+10+29*i))

        if self.pedir_palavra:
            texto_surf = self.fonte2.render("Escolha uma palavra:", True, 'white')
            self.screen.blit(texto_surf, (self.type_rect.x+10, self.type_rect.y+10))
            entrada_surf = self.fonte2.render(self.buffer_aux, True, 'white')
            largura = self.fonte2.size("Escolha uma palavra:")[0]
            self.screen.blit(entrada_surf, (self.type_rect.x+10+largura+10, self.type_rect.y+10))
        elif self.pedir_letra:
            texto_surf = self.fonte2.render("Escolha uma letra:", True, 'white')
            self.screen.blit(texto_surf, (self.type_rect.x+10, self.type_rect.y+10))
            entrada_surf = self.fonte2.render(self.buffer_aux, True, 'white')
            largura = self.fonte2.size("Escolha uma letra:")[0]
            self.screen.blit(entrada_surf, (self.type_rect.x+10+largura+10, self.type_rect.y+10))

        for i in range(len(self.jogadores)):
            jogador = self.jogadores[i]

            texto = f'Jogador {i+1}'
            texto += ' você' if self.numero == i + 1 else ''
            texto_surf = self.fonte2.render(texto, True, 'white')
            self.screen.blit(texto_surf, (self.players_rect.x+10, self.players_rect.y+10+100*i))

            texto_surf = self.fonte2.render(f'Vidas: {jogador["vidas"]}', True, 'white')
            self.screen.blit(texto_surf, (self.players_rect.x+10, self.players_rect.y+40+100*i))

            texto_surf = self.fonte2.render(f'Pontos: {jogador["pontos"]}', True, 'white')
            self.screen.blit(texto_surf, (self.players_rect.x+10, self.players_rect.y+70+100*i))

            pygame.draw.line(self.screen, 'white', (0, self.players_rect.y+10+97*(i+1)), (WIDTH*0.25, self.players_rect.y+10+97*(i+1)))

    def mostrar_resultado(self):
        s = pygame.Surface((WIDTH, HEIGHT))
        s.set_alpha(170)
        s.fill((0, 0, 0))
        self.screen.blit(s, (0, 0))
        
        numero_jogadores = len(self.jogadores)

        for i in range(numero_jogadores):
            jogador = self.jogadores[i]
            texto = f'Jogador {i+1}'
            largura = self.fonte1.size(texto)[0]
            x = (WIDTH-numero_jogadores*largura-100)/2+(largura+50)*i
            
            texto_surf = self.fonte1.render(texto, True, 'white')
            self.screen.blit(texto_surf, (x, 170))
            texto = f'{jogador["pontos"]} pontos'
            texto_surf = self.fonte1.render(texto, True, 'white')
            self.screen.blit(texto_surf, (x+10, 210))





jogo = Game()
jogo.desenhar_tela()

thread_receber_datagrama = threading.Thread(target=jogo.loop_receber)
thread_receber_datagrama.start()

while True:
    jogo.screen.fill('white')

    # jogo.receber_datagrama()
    
    if jogo.forcar_parada:
        pygame.quit()
        exit()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            jogo.forcar_parada = True
            jogo.conexao.close()
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:
            if jogo.pedir_palavra:
                if event.key == pygame.K_RETURN:
                    jogo.buffer = jogo.buffer_aux
                    jogo.buffer_aux = ''
                elif event.key == pygame.K_BACKSPACE:
                    jogo.buffer_aux = jogo.buffer_aux[:-1]
                else:                 
                    jogo.buffer_aux += event.unicode
            elif jogo.pedir_letra:
                if event.key == pygame.K_RETURN:
                    jogo.buffer = jogo.buffer_aux
                    jogo.buffer_aux = ''
                else:                 
                    jogo.buffer_aux = event.unicode
                    

    #   atualizar tela
    jogo.desenhar_tela()

    if jogo.finalizar:
        jogo.mostrar_resultado()

    pygame.display.update()

    jogo.clock.tick(60)