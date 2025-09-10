# app.py
from flask import (
    Flask, jsonify, render_template, request, session,
    g, redirect, url_for
)
import pymysql
from pymysql.cursors import DictCursor
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "troque-esta-chave")


DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASS = os.environ.get("DB_PASS", "")
DB_NAME = os.environ.get("DB_NAME", "bd_vozes")

def get_conn():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False
    )

# --------- Helpers p/ usuário logado (DEVEM vir antes das rotas) ---------
def get_user_by_id(user_id):
    if not user_id:
        return None
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, name, email FROM users WHERE id=%s", (user_id,))
        return cur.fetchone()

@app.before_request
def load_current_user():
    uid = session.get("user_id")
    g.current_user = get_user_by_id(uid) if uid else None

@app.context_processor
def inject_current_user():
    # Disponibiliza `current_user` em TODOS os templates
    return {"current_user": g.get("current_user")}

# (opcional) endpoint para o front saber se está logado
@app.get("/api/auth/me")
def whoami():
    uid = session.get("user_id")
    if not uid:
        return jsonify({"authenticated": False})
    return jsonify({"authenticated": True, "user_id": uid})

# ================== DADOS ESTÁTICOS (mapa) ==================
dados_dos_estados = {
    "ac":{"nome":"Acre","casos":39,"url_rede_ajuda":"https://www12.senado.leg.br/institucional/omv/pdfs/rede-ac.pdf"},
    "al":{"nome":"Alagoas","casos":97,"url_rede_ajuda":"https://www12.senado.leg.br/institucional/omv/pdfs/rede-al.pdf"},
    "ap":{"nome":"Amapá","casos":19,"url_rede_ajuda":"https://www12.senado.leg.br/institucional/omv/pdfs/rede-ap.pdf"},
    "am":{"nome":"Amazonas","casos":118,"url_rede_ajuda":"https://www12.senado.leg.br/institucional/omv/pdfs/rede-am.pdf"},
    "ba":{"nome":"Bahia","casos":243,"url_rede_ajuda":"https://www12.senado.leg.br/institucional/omv/pdfs/rede-ba.pdf"},
    "ce":{"nome":"Ceará","casos":104,"url_rede_ajuda":"https://www12.senado.leg.br/institucional/omv/pdfs/rede-ce.pdf"},
    "df":{"nome":"Distrito Federal","casos":85,"url_rede_ajuda":"https://www12.senado.leg.br/institucional/omv/pdfs/rede-df.pdf"},
    "es":{"nome":"Espírito Santo","casos":108,"url_rede_ajuda":"https://www12.senado.leg.br/institucional/omv/pdfs/rede-es.pdf"},
    "go":{"nome":"Goiás","casos":156,"url_rede_ajuda":"https://www12.senado.leg.br/institucional/omv/pdfs/rede-go.pdf"},
    "ma":{"nome":"Maranhão","casos":90,"url_rede_ajuda":"https://www12.senado.leg.br/institucional/omv/pdfs/rede-ma.pdf"},
    "mt":{"nome":"Mato Grosso","casos":220,"url_rede_ajuda":"https://www12.senado.leg.br/institucional/omv/pdfs/rede-mt.pdf"},
    "ms":{"nome":"Mato Grosso do Sul","casos":181,"url_rede_ajuda":"https://www12.senado.leg.br/institucional/omv/pdfs/rede/copy_of_rede-ms.pdf"},
    "mg":{"nome":"Minas Gerais","casos":366,"url_rede_ajuda":"https://www12.senado.leg.br/institucional/omv/pdfs/rede-mg.pdf"},
    "pa":{"nome":"Pará","casos":138,"url_rede_ajuda":"https://www12.senado.leg.br/institucional/omv/pdfs/rede-pa-1.pdf"},
    "pb":{"nome":"Paraíba","casos":90,"url_rede_ajuda":"https://www12.senado.leg.br/institucional/omv/pdfs/rede-pb.pdf"},
    "pr":{"nome":"Paraná","casos":346,"url_rede_ajuda":"https://www12.senado.leg.br/institucional/omv/pdfs/rede-pr.pdf"},
    "pe":{"nome":"Pernambuco","casos":146,"url_rede_ajuda":"https://www12.senado.leg.br/institucional/omv/pdfs/rede-pe.pdf"},
    "pi":{"nome":"Piauí","casos":98,"url_rede_ajuda":"https://www12.senado.leg.br/institucional/omv/pdfs/rede-pi.pdf"},
    "rj":{"nome":"Rio de Janeiro","casos":232,"url_rede_ajuda":"https://www12.senado.leg.br/institucional/omv/pdfs/rede-rj.pdf"},
    "rn":{"nome":"Rio Grande do Norte","casos":45,"url_rede_ajuda":"https://www12.senado.leg.br/institucional/omv/pdfs/rede-rn.pdf"},
    "rs":{"nome":"Rio Grande do Sul","casos":189,"url_rede_ajuda":"https://www12.senado.leg.br/institucional/omv/pdfs/rede-rs.pdf"},
    "ro":{"nome":"Rondônia","casos":98,"url_rede_ajuda":"https://www12.senado.leg.br/institucional/omv/pdfs/rede-ro.pdf"},
    "rr":{"nome":"Roraima","casos":25,"url_rede_ajuda":"https://www12.senado.leg.br/institucional/omv/pdfs/rede-rr.pdf"},
    "sc":{"nome":"Santa Catarina","casos":249,"url_rede_ajuda":"https://www12.senado.leg.br/institucional/omv/pdfs/rede-sc.pdf"},
    "sp":{"nome":"São Paulo","casos":540,"url_rede_ajuda":"https://www12.senado.leg.br/institucional/omv/pdfs/rede-sp.pdf"},
    "se":{"nome":"Sergipe","casos":32,"url_rede_ajuda":"https://www12.senado.leg.br/institucional/omv/pdfs/rede-se.pdf"},
    "to":{"nome":"Tocantins","casos":51,"url_rede_ajuda":"https://www12.senado.leg.br/institucional/omv/pdfs/rede-to.pdf"}
}

# ================== PÁGINAS ==================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/o-que-e")
def o_que_e():
    return render_template("o_que_e.html")

@app.route("/ajuda")
def ajuda():
    return render_template("ajuda.html")

@app.route("/leis")
def leis():
    return render_template("leis.html")

@app.route("/teste-de-risco")
def teste_de_risco():
    return render_template("teste_de_risco.html")

@app.route("/contato")
def contato():
    return render_template("contato.html")

# /cadastro: se estiver logado, redireciona pro teste
@app.route("/cadastro")
def cadastro_page():
    if g.current_user:
        return redirect(url_for("teste_de_risco"))
    return render_template("cadastro.html")

# ================== API MAPA (dados estáticos) ==================
@app.route("/api/estado/<string:sigla_estado>")
def get_estado_data(sigla_estado):
    estado = dados_dos_estados.get(sigla_estado.lower())
    return (jsonify(estado) if estado else (jsonify({"erro": "Estado não encontrado"}), 404))

# ================== AUTH ==================
@app.post("/api/auth/register")
def register():
    data = request.get_json(force=True)
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not all([name, email, password]):
        return jsonify({"error": "Campos obrigatórios: name, email, password"}), 400

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id FROM users WHERE email=%s", (email,))
        if cur.fetchone():
            return jsonify({"error": "E-mail já cadastrado"}), 409

        cur.execute(
            "INSERT INTO users (name,email,password_hash) VALUES (%s,%s,%s)",
            (name, email, generate_password_hash(password))
        )
        user_id = cur.lastrowid
        conn.commit()

    # login automático
    session["user_id"] = user_id
    return jsonify({"message": "Cadastro realizado e login efetuado", "user_id": user_id}), 201

@app.post("/api/auth/login")
def login():
    data = request.get_json(force=True)
    email = data.get("email"); password = data.get("password")
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, password_hash, is_active FROM users WHERE email=%s", (email,))
        row = cur.fetchone()
        if not row or not row["is_active"] or not check_password_hash(row["password_hash"], password):
            return jsonify({"error":"Credenciais inválidas"}), 401
        session["user_id"] = row["id"]
    return jsonify({"message":"Login realizado", "user_id": session["user_id"]})

@app.post("/api/auth/logout")
def logout():
    session.pop("user_id", None)
    return jsonify({"message":"Logout efetuado"})

# ================== CONTATO ==================
@app.post("/api/contact")
def send_contact():
    data = request.get_json(force=True)
    name = data.get("name"); email = data.get("email"); message = data.get("message")
    if not all([name, email, message]):
        return jsonify({"error":"Campos obrigatórios: name, email, message"}), 400
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO contact_messages (name,email,message) VALUES (%s,%s,%s)",
            (name, email, message)
        )
        conn.commit()
    return jsonify({"message":"Mensagem enviada"}), 201

# ================== TESTE DE RISCO ==================
@app.get("/api/risk/questions")
def risk_questions():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, code, question_text, weight, display_order FROM risk_questions ORDER BY display_order")
        return jsonify(cur.fetchall())

def classify_risk(total):
    if total >= 20: return "alto"
    if total >= 10: return "medio"
    return "baixo"

@app.post("/api/risk/submit")
def submit_risk():
    uid = session.get("user_id")
    if not uid:
        return jsonify({"error": "Necessário estar logado"}), 401

    payload = request.get_json(force=True)
    answers = payload.get("answers", [])
    q3a = bool(payload.get("q3a", False))
    if not answers:
        return jsonify({"error": "Envie answers[]"}), 400

    # 1) Carrega perguntas com code e display_order (em cache simples por request)
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT id, code, display_order
            FROM risk_questions
            ORDER BY display_order
        """)
        rows = cur.fetchall()
        # Mapas de apoio
        id_by_display = {i+1: r["id"] for i, r in enumerate(rows)}
        code_by_id    = {r["id"]: r["code"] for r in rows}

        # 2) Insere a submissão
        cur.execute(
            "INSERT INTO risk_responses (user_id, submitted_at) VALUES (%s,%s)",
            (uid, datetime.utcnow())
        )
        response_id = cur.lastrowid

        # 3) Fórmula igual à da UI
        # base: cada "Sim" = 1 ponto
        # extras: Q2(+4), Q3(+4), Q4(+3), Q5(+2), Q6(+2), Q7(+2), Q8(+1), Q9(+1)
        # regra especial: 3A -> -3
        # teto = 34
        extras_by_code = {
            "Q02": 4, "Q03": 4, "Q04": 3,
            "Q05": 2, "Q06": 2, "Q07": 2,
            "Q08": 1, "Q09": 1
        }
        MAXIMO = 34

        base = 0
        extras = 0

        # 4) Salva respostas e acumula pontuação
        for it in answers:
            qid = int(it["question_id"])
            ans = bool(it["answer_bool"])
            code = code_by_id.get(qid, "")  # "Q01".. "Q20"

            incr = 0
            if ans:
                incr = 1 + extras_by_code.get(code, 0)
                base += 1
                extras += extras_by_code.get(code, 0)

            # salva cada resposta com o score aplicado pela fórmula da UI
            cur.execute("""
                INSERT INTO risk_answers (response_id, question_id, answer_bool, score)
                VALUES (%s, %s, %s, %s)
            """, (response_id, qid, 1 if ans else 0, incr))

        if q3a:
            extras -= 3

        total = base + extras
        if total > MAXIMO:
            total = MAXIMO

        # 5) Classificação igual à UI
        # (0..7)   => "variavel" (você pode mapear como 'baixo' no BD)
        # (8..13)  => "aumentado" (mapear como 'medio')
        # (14..17) => "grave"     (mapear como 'alto')
        # (>=18)   => "extremo"   (precisa do enum ou mapear para 'alto')

        if total <= 7:
            level = "baixo"
        elif total <= 13:
            level = "medio"
        elif total <= 17:
            level = "alto"
        else:
            # se quiser guardar explicitamente "extremo", altere o ENUM no BD:
            # ALTER TABLE risk_results MODIFY risk_level ENUM('baixo','medio','alto','extremo') NOT NULL;
            level = "alto"  # ou "extremo" se você ampliar o enum

        cur.execute("""
            INSERT INTO risk_results (response_id, total_score, risk_level)
            VALUES (%s, %s, %s)
        """, (response_id, total, level))

        conn.commit()

    return jsonify({
        "message": "Teste salvo",
        "response_id": response_id,
        "total_score": total,
        "risk_level": level
    })


@app.get("/api/risk/history")
def risk_history():
    uid = session.get("user_id")
    if not uid:
        return jsonify({"error":"Necessário estar logado"}), 401
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT rr.id as response_id, rr.submitted_at, r.total_score, r.risk_level
            FROM risk_responses rr
            JOIN risk_results r ON r.response_id = rr.id
            WHERE rr.user_id=%s
            ORDER BY rr.submitted_at DESC
        """, (uid,))
        rows = cur.fetchall()
    for r in rows:
        r["submitted_at"] = r["submitted_at"].isoformat()
    return jsonify(rows)

# ================== RUN ==================
if __name__ == "__main__":
    app.run(debug=True)
