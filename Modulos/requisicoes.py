import urllib.request
import urllib.error
import json
import time
import base64

class Requisicoes:

    # Cache simples para armazenar respostas de GETs anteriores
    cache = {}

    @staticmethod
    def fazer_get(url, headers=None, params=None, timeout=10, retries=3, use_cache=True, proxy=None, auth=None):
        """
        Realiza uma requisição GET com várias opções.

        Parâmetros:
        url (str): A URL para a qual a requisição será enviada.
        headers (dict): Cabeçalhos adicionais para a requisição (opcional).
        params (dict): Parâmetros de consulta a serem adicionados à URL (opcional).
        timeout (int): Tempo limite da requisição em segundos (opcional, padrão 10s).
        retries (int): Número de tentativas em caso de falha (opcional, padrão 3).
        use_cache (bool): Se deve usar cache para respostas já feitas (opcional, padrão True).
        proxy (dict): Proxy para usar na requisição, se necessário (opcional).
        auth (dict): Dados de autenticação, como Token ou Basic Auth (opcional).
        
        Retorna:
        str: A resposta formatada da requisição (como texto).
        """
        # Montando a URL com os parâmetros de consulta, se existirem
        if params:
            url = Requisicoes._montar_url_com_params(url, params)

        # Verifica se a resposta já está em cache
        if use_cache and url in Requisicoes.cache:
            return Requisicoes.cache[url]
        
        # Cabeçalhos padrão
        if headers is None:
            headers = {}

        # Adiciona cabeçalhos de autenticação, se necessário
        if auth:
            headers.update(Requisicoes._adicionar_autenticacao(auth))

        # Configurações de proxy, se fornecido
        proxy_handler = None
        if proxy:
            proxy_handler = urllib.request.ProxyHandler(proxy)
        
        # Cria o opener com o proxy, se necessário
        opener = urllib.request.build_opener(proxy_handler) if proxy_handler else urllib.request.build_opener()

        # Tenta realizar a requisição com tentativas e timeout
        tentativa = 0
        while tentativa < retries:
            try:
                req = urllib.request.Request(url, headers=headers)
                with opener.open(req, timeout=timeout) as resposta:
                    dados = resposta.read().decode('utf-8')
                    resposta_formatada = Requisicoes._formatar_resposta(dados)
                    
                    # Armazena a resposta em cache
                    Requisicoes.cache[url] = resposta_formatada
                    return resposta_formatada

            except (urllib.error.HTTPError, urllib.error.URLError) as e:
                # Retorna mensagem de erro mais detalhada
                erro_msg = f"Erro: {e.reason}" if isinstance(e, urllib.error.URLError) else f"Erro HTTP: {e.code} - {e.reason}"
                if tentativa == retries - 1:
                    return erro_msg
                else:
                    tentativa += 1
                    time.sleep(2)  # Espera um tempo antes de tentar novamente

        return "Erro: Número máximo de tentativas atingido."

    @staticmethod
    def _montar_url_com_params(url, params):
        """
        Monta a URL com parâmetros de consulta.

        Parâmetros:
        url (str): A URL base para a qual os parâmetros serão adicionados.
        params (dict): Parâmetros de consulta para adicionar à URL.

        Retorna:
        str: A URL com os parâmetros de consulta.
        """
        if params:
            query_string = urllib.parse.urlencode(params)
            if '?' in url:
                return f"{url}&{query_string}"
            else:
                return f"{url}?{query_string}"
        return url

    @staticmethod
    def _adicionar_autenticacao(auth):
        """
        Adiciona o cabeçalho de autenticação, seja Bearer ou Basic.

        Parâmetros:
        auth (dict): O dicionário com as informações de autenticação.
        
        Retorna:
        dict: Cabeçalhos com autenticação.
        """
        headers = {}
        if 'token' in auth:
            headers['Authorization'] = f"Bearer {auth['token']}"
        elif 'username' in auth and 'password' in auth:
            base64_credentials = base64.b64encode(f"{auth['username']}:{auth['password']}".encode()).decode('utf-8')
            headers['Authorization'] = f"Basic {base64_credentials}"
        return headers

    @staticmethod
    def _formatar_resposta(resposta):
        """
        Formata a resposta JSON para texto normal ou exibe como está.

        Parâmetros:
        resposta (str): A resposta da requisição.

        Retorna:
        str: Resposta formatada de forma legível ou a string bruta.
        """
        try:
            dados = json.loads(resposta)
            return json.dumps(dados, indent=4, ensure_ascii=False)
        except json.JSONDecodeError:
            return resposta  # Caso não seja JSON, retorna o texto puro


