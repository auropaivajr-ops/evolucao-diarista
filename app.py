import streamlit as st
import json
import os
from openai import OpenAI

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Assistente de Declaração de Óbito", 
    page_icon="🩺", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INICIALIZAR CLIENTE OPENAI ---
@st.cache_resource
def get_openai_client():
    return OpenAI()

client = get_openai_client()

# --- CSS CUSTOMIZADO ---
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #f0f2f6;
        padding: 10px;
        text-align: center;
        font-size: 0.9rem;
        border-top: 1px solid #ddd;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
    }
    .suggestion-box {
        background-color: #e8f4f8;
        border-left: 4px solid #1f77b4;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- TÍTULO PRINCIPAL ---
st.markdown('<div class="main-header">📋 Assistente de Declaração de Óbito</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Sistema de Auxílio ao Preenchimento do Bloco V - Condições e Causas do Óbito</div>', unsafe_allow_html=True)

# --- LISTA DE GARBAGE CODES ---
GARBAGE_CODES = [
    "R99", "I46.9", "I50.9", "J96.9", "R09.2", "I51.9", "R57.9", 
    "I95.9", "R54", "I10", "E14.9", "N18.9", "J44.9", "I25.9",
    "I64", "C80.9", "K72.9", "N17.9", "I51.6", "R00.1"
]

# --- FUNÇÃO PARA VALIDAR GARBAGE CODES ---
def validar_garbage_code(codigo_cid):
    """Verifica se um código CID é um garbage code"""
    if not codigo_cid:
        return False, ""
    
    codigo_limpo = codigo_cid.strip().upper()
    
    for gc in GARBAGE_CODES:
        if codigo_limpo.startswith(gc):
            return True, f"⚠️ '{codigo_cid}' é um Garbage Code (código inespecífico). Considere usar um código mais específico."
    
    return False, "✅ Código válido"

# --- FUNÇÃO PARA GERAR SUGESTÃO COM IA ---
def gerar_sugestao_cadeia_causal(resumo_clinico):
    """Gera sugestão de preenchimento da cadeia causal usando IA"""
    
    if not resumo_clinico or len(resumo_clinico.strip()) < 20:
        return None
    
    # Lista de garbage codes para o prompt
    garbage_codes_str = ", ".join(GARBAGE_CODES)
    
    prompt = f"""Você é um assistente médico especializado em preenchimento de Declaração de Óbito (DO).

Com base no resumo clínico abaixo, sugira o preenchimento da cadeia causal do Bloco V da Declaração de Óbito, seguindo as normas do Ministério da Saúde do Brasil.

RESUMO CLÍNICO:
{resumo_clinico}

INSTRUÇÕES IMPORTANTES:
1. Identifique a cadeia causal seguindo a sequência lógica: Causa Imediata → Causa Intermediária → Causa Básica
2. Use APENAS códigos CID-10 válidos e específicos
3. EVITE os seguintes Garbage Codes (códigos inespecíficos): {garbage_codes_str}
4. A Causa Básica é a doença ou lesão que INICIOU a cadeia de eventos que levou ao óbito
5. A Causa Imediata é a condição que DIRETAMENTE causou o óbito
6. Causas Intermediárias são as condições entre a básica e a imediata
7. Parte II são condições que contribuíram mas não fazem parte da cadeia causal direta
8. Estime o tempo aproximado entre o início de cada condição e o óbito

RESPONDA APENAS NO FORMATO JSON ABAIXO (sem texto adicional):
{{
  "causa_imediata": {{
    "descricao": "descrição da causa imediata",
    "cid10": "código CID-10",
    "tempo": "tempo aproximado (ex: 2 dias, 6 horas)"
  }},
  "causa_intermediaria_b": {{
    "descricao": "descrição da causa intermediária b (se houver)",
    "cid10": "código CID-10 ou vazio",
    "tempo": "tempo aproximado ou vazio"
  }},
  "causa_intermediaria_c": {{
    "descricao": "descrição da causa intermediária c (se houver)",
    "cid10": "código CID-10 ou vazio",
    "tempo": "tempo aproximado ou vazio"
  }},
  "causa_basica": {{
    "descricao": "descrição da causa básica/original",
    "cid10": "código CID-10",
    "tempo": "tempo aproximado"
  }},
  "parte_ii": {{
    "descricao": "outras condições contribuintes (se houver)",
    "cid10": "códigos CID-10 separados por vírgula ou vazio"
  }},
  "justificativa": "breve explicação da lógica da cadeia causal"
}}"""

    try:
        with st.spinner("🤖 Analisando resumo clínico e gerando sugestão..."):
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "Você é um assistente médico especializado em Declaração de Óbito. Responda sempre em JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            resposta = response.choices[0].message.content.strip()
            
            # Remover possíveis marcadores de código
            if resposta.startswith("```json"):
                resposta = resposta[7:]
            if resposta.startswith("```"):
                resposta = resposta[3:]
            if resposta.endswith("```"):
                resposta = resposta[:-3]
            
            resposta = resposta.strip()
            
            # Parsear JSON
            sugestao = json.loads(resposta)
            return sugestao
            
    except Exception as e:
        st.error(f"❌ Erro ao gerar sugestão: {str(e)}")
        return None

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## 📚 Sobre o Sistema")
    st.markdown("""
    Este assistente foi desenvolvido para auxiliar médicos no preenchimento correto da **Declaração de Óbito (DO)**, 
    especialmente o **Bloco V** (Condições e Causas do Óbito).
    
    **Funcionalidades:**
    
    - ✅ Validação de Garbage Codes
    - ✅ Sugestão automática de cadeia causal com IA
    - ✅ Sugestão de sequência causal
    - ✅ Análise de qualidade
    - ✅ Orientações baseadas em manuais oficiais
    
    **Referências:**
    
    - Manual SVS/MS 2022
    - Lista de Garbage Codes 2024
    - CID-10
    """)
    
    st.markdown("---")
    st.markdown("## 🔒 Privacidade")
    st.warning("""
    ⚠️ **NUNCA** insira dados reais de pacientes (nomes, CPF, etc.). Use apenas informações clínicas anônimas.
    """)

# --- ABAS PRINCIPAIS ---
tab1, tab2, tab3 = st.tabs(["🛠️ Assistente de Preenchimento", "📚 Exemplos Práticos", "⚠️ Avisos Legais e Privacidade"])

# --- ABA 1: ASSISTENTE DE PREENCHIMENTO ---
with tab1:
    st.markdown("""
    Este assistente auxilia na organização da **cadeia causal do Bloco V**, filtrando *Garbage Codes* e sugerindo a sequência lógica 
    conforme as normas do Ministério da Saúde.
    """)
    
    st.markdown("---")
    
    # Resumo Clínico
    st.markdown("### 📝 Resumo Clínico (Anônimo)")
    resumo_clinico = st.text_area(
        "Cole aqui o resumo clínico do caso (sem identificação do paciente):",
        height=150,
        placeholder="Exemplo: Paciente idoso, sexo masculino, com histórico de DPOC há 10 anos, internado por pneumonia bacteriana há 5 dias, evoluiu com insuficiência respiratória e choque séptico..."
    )
    
    # Botão para gerar sugestão
    if st.button("🤖 Gerar Sugestão Automática com IA", type="primary"):
        if resumo_clinico and len(resumo_clinico.strip()) >= 20:
            sugestao = gerar_sugestao_cadeia_causal(resumo_clinico)
            
            if sugestao:
                st.session_state['sugestao_gerada'] = sugestao
                st.success("✅ Sugestão gerada com sucesso!")
        else:
            st.warning("⚠️ Por favor, insira um resumo clínico com pelo menos 20 caracteres.")
    
    # Exibir sugestão se foi gerada
    if 'sugestao_gerada' in st.session_state:
        sugestao = st.session_state['sugestao_gerada']
        
        st.markdown("---")
        st.markdown("### 💡 Sugestão Gerada pela IA")
        
        st.markdown('<div class="suggestion-box">', unsafe_allow_html=True)
        
        # Causa Imediata
        st.markdown("**a) Causa Imediata/Terminal:**")
        st.info(f"**{sugestao['causa_imediata']['descricao']}** - CID: {sugestao['causa_imediata']['cid10']} - Tempo: {sugestao['causa_imediata']['tempo']}")
        is_gc, msg = validar_garbage_code(sugestao['causa_imediata']['cid10'])
        if is_gc:
            st.warning(msg)
        
        # Causa Intermediária B
        if sugestao['causa_intermediaria_b']['descricao']:
            st.markdown("**b) Causa Intermediária:**")
            st.info(f"**{sugestao['causa_intermediaria_b']['descricao']}** - CID: {sugestao['causa_intermediaria_b']['cid10']} - Tempo: {sugestao['causa_intermediaria_b']['tempo']}")
            is_gc, msg = validar_garbage_code(sugestao['causa_intermediaria_b']['cid10'])
            if is_gc:
                st.warning(msg)
        
        # Causa Intermediária C
        if sugestao['causa_intermediaria_c']['descricao']:
            st.markdown("**c) Causa Intermediária:**")
            st.info(f"**{sugestao['causa_intermediaria_c']['descricao']}** - CID: {sugestao['causa_intermediaria_c']['cid10']} - Tempo: {sugestao['causa_intermediaria_c']['tempo']}")
            is_gc, msg = validar_garbage_code(sugestao['causa_intermediaria_c']['cid10'])
            if is_gc:
                st.warning(msg)
        
        # Causa Básica
        st.markdown("**d) Causa Básica/Original:**")
        st.info(f"**{sugestao['causa_basica']['descricao']}** - CID: {sugestao['causa_basica']['cid10']} - Tempo: {sugestao['causa_basica']['tempo']}")
        is_gc, msg = validar_garbage_code(sugestao['causa_basica']['cid10'])
        if is_gc:
            st.warning(msg)
        
        # Parte II
        if sugestao['parte_ii']['descricao']:
            st.markdown("**Parte II - Outras Condições:**")
            st.info(f"**{sugestao['parte_ii']['descricao']}** - CID: {sugestao['parte_ii']['cid10']}")
        
        # Justificativa
        st.markdown("**📋 Justificativa da Cadeia Causal:**")
        st.success(sugestao['justificativa'])
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.info("💡 **Dica:** Você pode editar e ajustar a sugestão acima conforme necessário. Sempre revise criticamente antes de usar.")
    
    st.markdown("---")
    
    # Formulário manual (mantido para edição)
    st.markdown("### 📊 Parte I: Cadeia Causal")
    st.info("⚠️ Preencha da consequência final (a) até a causa original (d). A última linha preenchida será considerada a **Causa Básica**.")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        causa_a = st.text_input("a) Causa Imediata/Terminal", placeholder="Ex: Choque séptico")
    with col2:
        tempo_a = st.text_input("Tempo (a)", placeholder="Ex: 2 dias")
    
    if causa_a:
        is_garbage, mensagem = validar_garbage_code(causa_a)
        if is_garbage:
            st.warning(mensagem)
        else:
            st.success(mensagem)
    
    st.markdown("*Devido ou como consequência de:*")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        causa_b = st.text_input("b) Causa Intermediária", placeholder="Ex: Pneumonia bacteriana")
    with col2:
        tempo_b = st.text_input("Tempo (b)", placeholder="Ex: 7 dias")
    
    if causa_b:
        is_garbage, mensagem = validar_garbage_code(causa_b)
        if is_garbage:
            st.warning(mensagem)
        else:
            st.success(mensagem)
    
    st.markdown("*Devido ou como consequência de:*")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        causa_c = st.text_input("c) Causa Intermediária (opcional)", placeholder="Ex: DPOC")
    with col2:
        tempo_c = st.text_input("Tempo (c)", placeholder="Ex: 10 anos")
    
    if causa_c:
        is_garbage, mensagem = validar_garbage_code(causa_c)
        if is_garbage:
            st.warning(mensagem)
        else:
            st.success(mensagem)
    
    st.markdown("*Devido ou como consequência de:*")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        causa_d = st.text_input("d) Causa Básica/Original", placeholder="Ex: Tabagismo")
    with col2:
        tempo_d = st.text_input("Tempo (d)", placeholder="Ex: 30 anos")
    
    if causa_d:
        is_garbage, mensagem = validar_garbage_code(causa_d)
        if is_garbage:
            st.warning(mensagem)
        else:
            st.success(mensagem)
    
    st.markdown("---")
    st.markdown("### 📊 Parte II: Outras Condições Contribuintes")
    st.info("Condições significativas que contribuíram para o óbito, mas não fazem parte da cadeia causal direta.")
    
    parte_ii = st.text_area(
        "Outras condições (Parte II)",
        placeholder="Ex: Hipertensão arterial sistêmica, Diabetes mellitus tipo 2",
        height=80
    )
    
    if parte_ii:
        codigos_parte_ii = [c.strip() for c in parte_ii.split(',')]
        for codigo in codigos_parte_ii:
            is_garbage, mensagem = validar_garbage_code(codigo)
            if is_garbage:
                st.warning(f"{codigo}: {mensagem}")

# --- ABA 2: EXEMPLOS PRÁTICOS ---
with tab2:
    st.markdown("## 📚 Exemplos Práticos de Preenchimento")
    
    st.markdown("### Exemplo 1: Óbito por Complicação de Doença Crônica")
    st.code("""
Resumo: Paciente idoso, diabético há 15 anos, internado por pneumonia bacteriana 
há 7 dias, evoluiu com choque séptico e óbito.

Preenchimento:
a) Causa Imediata: Choque séptico (CID A41.9) - Tempo: 2 dias
b) Causa Intermediária: Pneumonia bacteriana (CID J15.9) - Tempo: 7 dias
c) Causa Básica: Diabetes mellitus tipo 2 (CID E11.9) - Tempo: 15 anos

Parte II: Hipertensão arterial sistêmica (CID I10), Obesidade (CID E66.9)
    """)
    
    st.markdown("### Exemplo 2: Óbito por Acidente de Trânsito")
    st.code("""
Resumo: Vítima de acidente automobilístico, traumatismo cranioencefálico grave, 
evoluiu com edema cerebral e herniação.

Preenchimento:
a) Causa Imediata: Herniação cerebral (CID G93.5) - Tempo: 6 horas
b) Causa Intermediária: Edema cerebral (CID G93.6) - Tempo: 12 horas
c) Causa Básica: Traumatismo cranioencefálico - acidente de trânsito (CID S06.9) - Tempo: 1 dia

Parte II: (vazio, se não houver condições prévias relevantes)
    """)

# --- ABA 3: AVISOS LEGAIS ---
with tab3:
    st.markdown("## ⚠️ Avisos Legais e Privacidade")
    
    st.error("""
    ### 🔒 PRIVACIDADE E PROTEÇÃO DE DADOS
    
    - **NUNCA** insira dados reais de pacientes (nomes, CPF, endereços, números de prontuário, etc.)
    - Use **APENAS** informações clínicas anônimas e resumidas
    - Este sistema **NÃO armazena** dados permanentemente
    - Todas as informações são processadas em tempo real e descartadas após o uso
    """)
    
    st.warning("""
    ### 📜 RESPONSABILIDADE PROFISSIONAL
    
    - Este é um **assistente de apoio à decisão**, não substitui o julgamento clínico
    - A **responsabilidade final** pelo preenchimento correto da DO é do **médico atestante**
    - Sempre consulte os **manuais oficiais** em casos de dúvida
    - As sugestões geradas pela IA devem ser **revisadas criticamente**
    """)
    
    st.info("""
    ### 📚 REFERÊNCIAS OFICIAIS
    
    - Manual de Instruções para o Preenchimento da Declaração de Óbito (SVS/MS 2022)
    - Lista de Garbage Codes 2024
    - Classificação Internacional de Doenças - 10ª Revisão (CID-10)
    - Portarias e normas técnicas do Ministério da Saúde
    """)

# --- RODAPÉ ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px; color: #666;">
    <p><strong>Desenvolvido por Manus IA e Dr. Auro Júnior</strong></p>
    <p>Instagram: <a href="https://www.instagram.com/auropaiva/" target="_blank">@auropaiva</a></p>
</div>
""", unsafe_allow_html=True)
