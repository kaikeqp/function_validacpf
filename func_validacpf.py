import azure.functions as func
import logging
import re

app = func.FunctionApp()

def validar_cpf(cpf: str) -> dict:
    """
    Valida um CPF brasileiro
    
    Args:
        cpf (str): CPF a ser validado
    
    Returns:
        dict: Dicionário com resultado da validação
    """
    
    # Remove caracteres não numéricos
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        return {
            "valido": False,
            "erro": "CPF deve conter 11 dígitos",
            "cpf_formatado": None
        }
    
    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        return {
            "valido": False,
            "erro": "CPF não pode ter todos os dígitos iguais",
            "cpf_formatado": None
        }
    
    # Calcula primeiro dígito verificador
    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)
    
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    if digito1 != int(cpf[9]):
        return {
            "valido": False,
            "erro": "Primeiro dígito verificador inválido",
            "cpf_formatado": None
        }
    
    # Calcula segundo dígito verificador
    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)
    
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    if digito2 != int(cpf[10]):
        return {
            "valido": False,
            "erro": "Segundo dígito verificador inválido",
            "cpf_formatado": None
        }
    
    # Formata CPF
    cpf_formatado = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    
    return {
        "valido": True,
        "erro": None,
        "cpf_formatado": cpf_formatado,
        "cpf_apenas_numeros": cpf
    }

@app.function_name(name="ValidarCPF")
@app.route(route="validar-cpf", methods=["POST"])
def validar_cpf_http(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function para validar CPF via HTTP
    """
    logging.info('Python HTTP trigger function processed a request.')
    
    try:
        # Obtém o CPF do corpo da requisição
        req_body = req.get_json()
        cpf = req_body.get('cpf')
        
        if not cpf:
            return func.HttpResponse(
                '{"erro": "CPF não fornecido no corpo da requisição"}',
                status_code=400,
                mimetype="application/json"
            )
        
        # Valida o CPF
        resultado = validar_cpf(cpf)
        
        return func.HttpResponse(
            json.dumps(resultado),
            status_code=200 if resultado["valido"] else 400,
            mimetype="application/json"
        )
        
    except ValueError:
        return func.HttpResponse(
            '{"erro": "Corpo da requisição inválido"}',
            status_code=400,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Erro interno: {str(e)}")
        return func.HttpResponse(
            '{"erro": "Erro interno do servidor"}',
            status_code=500,
            mimetype="application/json"
        )

# Função adicional para validação via GET
@app.function_name(name="ValidarCPFGet")
@app.route(route="validar-cpf-get", methods=["GET"])
def validar_cpf_get(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function para validar CPF via GET
    """
    logging.info('Python HTTP trigger function processed a GET request.')
    
    cpf = req.params.get('cpf')
    
    if not cpf:
        return func.HttpResponse(
            '{"erro": "Parâmetro CPF não fornecido. Use ?cpf=12345678901"}',
            status_code=400,
            mimetype="application/json"
        )
    
    # Valida o CPF
    resultado = validar_cpf(cpf)
    
    return func.HttpResponse(
        json.dumps(resultado),
        status_code=200 if resultado["valido"] else 400,
        mimetype="application/json"
    )