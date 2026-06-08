import os
from dotenv import load_dotenv
import psycopg2

# Carrega as variáveis salvas no arquivo .env
load_dotenv()


def testar_conexao_supabase():
    print("🔄 Tentando conectar ao Supabase...")

    try:
        # Puxa a string de conexão direto do cofre oculto
        db_url = os.getenv("DB_URL")

        # Conecta no PostgreSQL
        conexao = psycopg2.connect(db_url)
        cursor = conexao.cursor()

        # Executa uma query simples de teste no banco da nuvem
        cursor.execute("SELECT version();")
        versao = cursor.fetchone()

        print("\n================ CONEXÃO BEM-SUCEDIDA! ================")
        print(f"PostgreSQL Versão: {versao[0]}")
        print("=======================================================")

        cursor.close()
        conexao.close()

    except Exception as e:
        print(f"\n❌ Erro crítico ao conectar no banco de dados: {e}")


if __name__ == "__main__":
    testar_conexao_supabase()