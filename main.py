# Obs.: Escrevi o código no VSCode e quando fui passar para o Google Colab ele não estava rodando corretamente. Porém, aqui no Repl.it ele não possui problemas.

from threading import Thread, Condition
from queue import Queue
from time import sleep, time_ns

# Configurações do programa
max_pedidos_garcom_default = 10
amount_garcons = 10
time_fazer_pedido = 0.1
time_prepara_pedido = 0.1
time_entregar_pedido = 0.1
time_wait_expire = 0.1

counter = 0  # Contador para criar os ids dos pedidos
delta_time = 0  # Timer para a operação da cozinha

lista_pedidos = Queue(4)
lista_prontos = Queue()

condition_pedidos = Condition()
condition_prontos = Condition()

pedidos = list()

is_all_finished = False  # Flag para indicar que tudo já foi finalizado
# Flag para indicar se já foi executado a função mostrar_logs() (execução final do programa)
is_printed = False


def verify_is_all_finished():  # Verifica se já acabou tudo
    global pedidos, is_all_finished, delta_time
    num_pedidos_finished = 0
    for pedido in pedidos:
        if pedido.garcom_entregou != None:
            num_pedidos_finished += 1
    if num_pedidos_finished >= max_pedidos_garcom_default * amount_garcons:
        is_all_finished = True
        delta_time += time_ns()  # Termina o cálculo de tempo (não leva em conta as impressões a seguir)
        Thread(target=mostrar_logs).start()
    else:
        is_all_finished = False


def mostrar_logs():  # Função para mostrar os logs após todos terminarem
    global pedidos, delta_time, is_printed
    sleep(2.5) # Tempo para garantir que todas as threads já detectaram o encerramento pela flag
    with condition_pedidos:
        with condition_prontos:
            print("\nImprimindo log dos pedidos...\n")
            print("ID\tG atendeu\tCozinheiro\tG entregou")
            for pedido in pedidos:
                pedido.mostrar()
            print(f"\nForam {len(pedidos)} pedidos")
            print(
                f"\nFoi gasto {delta_time/1_000_000_000:.2f}s ({delta_time}ns)")
    is_printed = True


class Garcom:
    __thread = None
    __id = None
    __max_pedidos = None

    def __init__(self, id: int, max_pedidos: int):
        self.__thread = Thread(target=self.fazer_pedido, args=[])
        self.__id = id
        self.__max_pedidos = max_pedidos

    def start(self):
        self.__thread.start()

    def stop(self):
        self.__thread.join()

    def fazer_pedido(self):
        global lista_pedidos, counter, pedidos  # flags_finished_garcons, counter
        for i in range(self.__max_pedidos):  # Gera sua parte de pedidos
            with condition_pedidos:
                while lista_pedidos.full():  # Espera se a lista estiver cheia
                    condition_pedidos.wait(time_wait_expire)

                sleep(time_fazer_pedido)
                pedido = Pedido(counter + 1, self.__id)
                lista_pedidos.put(pedido)
                pedidos.append(pedido)
                #print(f"Pedido {pedido.id:0>2} atendido pelo garçom {pedido.garcom_atendeu:0>2}")

                counter += 1
                condition_pedidos.notify(n=1)

            self.levar_pedido()  # Tenta levar pedido

        while not is_all_finished:  # Fica tentando levar pedidos após terminar sua parte
            self.levar_pedido()

        #print(f"Garçom {self.__id:0>2} terminou")

    def levar_pedido(self):  # Tenta levar pedidos já preparados
        if not lista_prontos.empty():  # Primeira verificação superficial para não perder tempo adquirindo a condição por nada
            with condition_prontos:
                if not lista_prontos.empty():  # Segunda verificação para garantir que no meio tempo (na aquisição da condição) ela não ficou vazia
                    pronto = lista_prontos.get()
                    sleep(time_entregar_pedido)
                    pronto.entregue(self.__id)
                    #print(f"Pedido {pronto.id:0>2} entregue pelo garçom {pronto.garcom_entregou:0>2}")
                    verify_is_all_finished()  # Verifica se já acabou tudo
                condition_prontos.notify(n=1)


class Cozinheiro:
    __thread = None
    __id = None

    def __init__(self, id: int):
        self.__thread = Thread(target=self.prepara_pedido, args=[])
        self.__id = id

    def start(self):
        self.__thread.start()

    def stop(self):
        self.__thread.join()

    def prepara_pedido(self):
        global lista_pedidos, is_all_finished
        while True:
            with condition_pedidos:
                while lista_pedidos.empty(
                ) and not is_all_finished:  # Espera se não há pedidos pendentes
                    condition_pedidos.wait(time_wait_expire)
                if lista_pedidos.empty(
                ) and is_all_finished:  # Com todos os garçons já terminados, então termina
                    break

                pedido = lista_pedidos.get()
                condition_pedidos.notify(n=1)
                sleep(time_prepara_pedido)

                with condition_prontos:
                    pedido.preparado(self.__id)
                    lista_prontos.put(pedido)
                    condition_prontos.notify(n=1)
                    #print(f"Pedido {pedido.id:0>2} preparado pelo cozinheiro {pedido.cozinheiro_preparou:0>2}")

        #print(f"Cozinheiro {self.__id:0>2} terminou")


class Pedido:
    id = None
    garcom_atendeu = None
    cozinheiro_preparou = None
    garcom_entregou = None

    def __init__(self, id, garcom_atendeu):
        self.id = id
        self.garcom_atendeu = garcom_atendeu

    def preparado(self, cozinheiro_preparou):
        self.cozinheiro_preparou = cozinheiro_preparou

    def entregue(self, garcom_entregou):
        self.garcom_entregou = garcom_entregou

    def mostrar(self):
        print(
            f"{self.id:0>2}\t{self.garcom_atendeu:0>2}\t\t{self.cozinheiro_preparou:0>2}\t\t{self.garcom_entregou:0>2}"
        )


if __name__ == "__main__":
    print("Iniciando programa...")

    # Com apenas um cozinheiro
    print("\n\nCom apenas um cozinheiro:")
    amount_cozinheiros = 1
    garcons = [
        Garcom(i + 1, max_pedidos_garcom_default) for i in range(amount_garcons)
    ]
    cozinheiros = [Cozinheiro(i + 1) for i in range(amount_cozinheiros)]
    delta_time -= time_ns()
    for cozinheiro in cozinheiros:
        cozinheiro.start()

    for garcom in garcons:
        garcom.start()

    # Aguarda fim da primeira execução
    while not is_printed:
        sleep(1)

    # Reset das variáveis
    counter = 0
    delta_time = 0
    pedidos = list()
    is_all_finished = False
    is_printed = False

    # Com dois cozinheiros
    print("\n\nCom dois cozinheiros:")
    amount_cozinheiros = 2
    garcons = [
        Garcom(i + 1, max_pedidos_garcom_default) for i in range(amount_garcons)
    ]
    cozinheiros = [Cozinheiro(i + 1) for i in range(amount_cozinheiros)]
    delta_time -= time_ns()
    for cozinheiro in cozinheiros:
        cozinheiro.start()

    for garcom in garcons:
        garcom.start()

    # Aguarda fim da segunda execução
    while not is_printed:
        sleep(1)
