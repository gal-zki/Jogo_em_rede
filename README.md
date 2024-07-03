# Jogo em rede

---------
# FUNCIONAMENTO	
O programa é feito para que seja executado uma instância do servidor e 3 instâncias de clientes. Os clientes disputam entre si em 3 rodadas para ver quem faz mais pontos. 

Em cada rodada, o cliente da rodada escolhe uma palavra e os outros clientes alternam entre si chutando letras para a palavra secreta. Caso o cliente acerte a letra, ele ganha o número de pontos igual ao número de ocorrências da letra na palavra e pode chutar uma letra novamente. Caso ele erre, ele perde uma vida, o cliente da rodada ganha 1 ponto e o outro cliente começa sua vez.

Quando a palavra for totalmente revelada, a rodada acaba e as variáveis de controle de rodada são reiniciadas. Se um jogador perde todas as suas vidas, ele não participa mais pelo resto da rodada. Se a palavra não foi revelada, mas todos os jogadores perderam todas as suas vidas, a rodada acaba também. 
  
Quando o jogo acaba, é mostrada uma tela com a pontuação final de cada jogador. O jogador da rodada pode finalizar o jogo prematuramente enviando "/q" no momento de escolher a palavra. Nesse caso, todos os clientes vão para a tela de resultados. Nessa tela, pode fechar o jogo clicando no "X" da janela e entrando com ENTER no servidor.

-----------

# MENSAGENS TROCADAS
  A troca de mensagens é bastante simples e intuitiva. Toda mensagem a ser enviada começa pelo seu tamanho e depois o texto. Exemplo: "02oi". 
  
  O servidor sempre sabe o que ele está recebendo, portanto, todas as mensagens enviadas pelos clientes são apenas o texto com a informação (palavra, letra do chute). 
  
  O cliente não tem o mesmo luxo. Por conta disso, o servidor envia a mensagem no formato "{tipo}{informação}" e o cliente faz a decodificação e chama a rotina correspondente.

# Alguns exemplos de mensagem:

"/palavra" 	        - para pedir uma palavra;

"/letra{segredo*}" 	- pede uma letra;

"/i{numero}"	        - manda o número do jogador;

"/s{segredo*}"		- envia o estado atual da palavra secreta;

"/e{n1}{v1}{p1}..{p3}"	- envia o estado atual dos jogadores, onde n1 é o número do jogador 1, v1 é o seu número de vidas, p1 é sua quantidade de pontos e p3 é a quantidade de pontos do jogador 3. Na mesma mensagem são enviadas as informações de todos os jogadores;
			  
"/resultado"		- sinaliza para os clientes que o jogo acabou e que agora é para mostrar os resultados na tela.












	
