import mercadopago
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import os
import webbrowser

app = Flask(__name__)
CORS(app)  # Permite requisições do frontend React

# Token do Mercado Pago (substitua pelo seu token real)
ACCESS_TOKEN = "APP_USR-5104821592879776-070416-cbb168c44c90b05b9ac4320dc0e10e7e-2489255518"

def gerar_pix(valor, email="cliente@example.com", nome="Cliente", sobrenome="Pagador"):
    try:
        # Inicializa o SDK do Mercado Pago
        sdk = mercadopago.SDK(ACCESS_TOKEN)
        
        # Dados do pagamento PIX
        payment_data = {
            "transaction_amount": float(valor),
            "payment_method_id": "pix",
            "description": "Pagamento Bobbie Goods - Livros de Colorir",
            "date_of_expiration": (datetime.now() + timedelta(minutes=30)).strftime('%Y-%m-%dT%H:%M:%S.000-03:00'),
            "payer": {
                "email": email,
                "first_name": nome,
                "last_name": sobrenome,
                "identification": {
                    "type": "CPF", 
                    "number": "12345678909"
                }
            }
        }

        print("⏳ Criando pagamento PIX...")
        
        # Cria o pagamento
        payment_response = sdk.payment().create(payment_data)
        
        if payment_response["status"] in [200, 201]:
            print("\n✅ PIX gerado com sucesso!")
            
            # Extrai os dados do PIX
            pix_info = payment_response["response"]["point_of_interaction"]["transaction_data"]
            
            print(f"💰 Valor: R$ {payment_data['transaction_amount']}")
            print(f"🆔 ID do Pagamento: {payment_response['response']['id']}")
            print(f"📅 Expira em: {payment_response['response']['date_of_expiration']}")
            print(f"📋 Código PIX: {pix_info['qr_code']}")
            print(f"🔗 Link para pagamento: {pix_info['ticket_url']}")
            
            # Cria um arquivo HTML com o QR Code
            html_filename = f"pix_payment_{payment_response['response']['id']}.html"
            with open(html_filename, "w", encoding='utf-8') as f:
                f.write(f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Pagamento PIX - Bobbie Goods</title>
                    <meta charset="UTF-8">
                    <style>
                        body {{ 
                            font-family: 'Comic Neue', Arial, sans-serif; 
                            text-align: center; 
                            margin-top: 50px; 
                            background: linear-gradient(135deg, #FF9A8B, #FF6B95);
                            color: white;
                            min-height: 100vh;
                        }}
                        .container {{
                            background: white;
                            color: #333;
                            max-width: 500px;
                            margin: 0 auto;
                            padding: 30px;
                            border-radius: 20px;
                            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                        }}
                        h1 {{ color: #FF6B95; margin-bottom: 20px; }}
                        .qrcode {{ 
                            margin: 20px auto; 
                            border: 3px solid #FF6B95;
                            border-radius: 10px;
                            padding: 10px;
                            background: white;
                        }}
                        .info {{ 
                            margin: 15px 0; 
                            font-size: 18px; 
                            padding: 10px;
                            background: #f8f9fa;
                            border-radius: 10px;
                        }}
                        .pix-code {{
                            background: #e9ecef;
                            padding: 15px;
                            border-radius: 10px;
                            font-family: monospace;
                            word-break: break-all;
                            font-size: 12px;
                            margin: 20px 0;
                        }}
                        .copy-btn {{
                            background: #FF6B95;
                            color: white;
                            border: none;
                            padding: 10px 20px;
                            border-radius: 25px;
                            cursor: pointer;
                            font-weight: bold;
                            margin-top: 10px;
                        }}
                        .copy-btn:hover {{
                            background: #FF9A8B;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>🎨 Pagamento PIX - Bobbie Goods</h1>
                        <div class="info">💰 Valor: R$ {payment_data['transaction_amount']:.2f}</div>
                        <img class="qrcode" src="data:image/png;base64,{pix_info['qr_code_base64']}" alt="QR Code PIX">
                        <div class="info">⏳ Expira em: {payment_response['response']['date_of_expiration']}</div>
                        <div class="info">🆔 ID: {payment_response['response']['id']}</div>
                        
                        <div class="pix-code">
                            <strong>📋 Código PIX Copia e Cola:</strong><br>
                            {pix_info['qr_code']}
                        </div>
                        
                        <button class="copy-btn" onclick="copyPixCode()">📋 Copiar Código PIX</button>
                        <br><br>
                        <a href="{pix_info['ticket_url']}" target="_blank" style="color: #FF6B95; text-decoration: none; font-weight: bold;">
                            🔗 Abrir link para pagamento
                        </a>
                    </div>
                    
                    <script>
                        function copyPixCode() {{
                            const pixCode = "{pix_info['qr_code']}";
                            navigator.clipboard.writeText(pixCode).then(() => {{
                                alert('Código PIX copiado para a área de transferência! 🎨');
                            }});
                        }}
                    </script>
                </body>
                </html>
                """)
            
            print(f"\n📄 Arquivo '{html_filename}' gerado com o QR Code!")
            
            # Abre o arquivo no navegador (opcional no servidor)
            # webbrowser.open(html_filename)
            
            return {
                "success": True,
                "data": {
                    "id": payment_response['response']['id'],
                    "qr_code": pix_info['qr_code'],
                    "qr_code_base64": pix_info['qr_code_base64'],
                    "ticket_url": pix_info['ticket_url'],
                    "date_of_expiration": payment_response['response']['date_of_expiration'],
                    "transaction_amount": payment_data['transaction_amount'],
                    "html_file": html_filename
                }
            }
            
        else:
            print("\n❌ Erro ao gerar PIX:")
            print(f"Código: {payment_response['status']}")
            print(f"Mensagem: {payment_response['response']['message']}")
            if 'cause' in payment_response['response']:
                for cause in payment_response['response']['cause']:
                    print(f" - {cause['description']}")
            
            return {
                "success": False,
                "error": f"Erro {payment_response['status']}: {payment_response['response']['message']}"
            }
    
    except Exception as e:
        print(f"\n⚠️ Erro inesperado: {str(e)}")
        return {
            "success": False,
            "error": f"Erro inesperado: {str(e)}"
        }

@app.route('/')
def index():
    return jsonify({
        "message": "🎨 API Bobbie Goods PIX - Funcionando!",
        "endpoints": {
            "gerar_pix": "/gerar-pix [POST]",
            "status": "/status [GET]"
        }
    })

@app.route('/gerar-pix', methods=['POST'])
def gerar_pix_endpoint():
    try:
        data = request.get_json()
        
        valor = data.get('valor', 10.00)
        email = data.get('email', 'cliente@example.com')
        nome = data.get('nome', 'Cliente')
        sobrenome = data.get('sobrenome', 'Pagador')
        
        print(f"\n🎨 Nova solicitação PIX:")
        print(f"💰 Valor: R$ {valor}")
        print(f"📧 Email: {email}")
        print(f"👤 Nome: {nome} {sobrenome}")
        
        resultado = gerar_pix(valor, email, nome, sobrenome)
        
        return jsonify(resultado)
        
    except Exception as e:
        print(f"⚠️ Erro no endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Erro no servidor: {str(e)}"
        }), 500

@app.route('/status')
def status():
    return jsonify({
        "status": "online",
        "service": "Bobbie Goods PIX API",
        "mercadopago_token": "configurado" if ACCESS_TOKEN else "não configurado",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook para receber notificações do Mercado Pago"""
    try:
        data = request.get_json()
        print(f"\n🔔 Webhook recebido: {data}")
        
        # Aqui você processaria as notificações do Mercado Pago
        # Por exemplo, atualizar status do pedido quando o pagamento for confirmado
        
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        print(f"⚠️ Erro no webhook: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("🎨 Iniciando servidor Bobbie Goods PIX...")
    print("🔗 Acesse: http://localhost:5000")
    print("📋 Documentação: http://localhost:5000")
    print("💳 Endpoint PIX: http://localhost:5000/gerar-pix")
    app.run(debug=True, host='0.0.0.0', port=5000)
