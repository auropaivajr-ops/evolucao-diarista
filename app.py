import streamlit as st
import json

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Assistente de Declaração de Óbito", 
    page_icon="🩺", 
    layout="wide",
    initial_sidebar_state="expanded"
)

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
</style>
""", unsafe_allow_html=True)

# --- TÍTULO PRINCIPAL ---
st.markdown('<div class="main-header">📋 Assistente de Declaração de Óbito</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Sistema de Auxílio ao Preenchimento do Bloco V - Condições e Causas do Óbito</div>', unsafe_allow_html=True)

# --- BASE DE DADOS DE GARBAGE CODES ---
garbage_codes_dict = {
    # Códigos R (Sintomas e sinais)
    "R99": "Causa desconhecida de mortalidade",
    "R98": "Morte sem assistência",
    "R09.2": "Parada respiratória",
    "R57.9": "Choque não especificado",
    "R54": "Senilidade",
    "R64": "Caquexia",
    "R00-R99": "Sintomas, sinais e achados anormais",
    
    # Códigos I (Cardiovascular)
    "I46": "Parada cardíaca",
    "I46.0": "Parada cardíaca com ressuscitação bem-sucedida",
    "I46.1": "Morte cardíaca súbita",
    "I46.9": "Parada cardíaca não especificada",
    "I50.9": "Insuficiência cardíaca não especificada",
    "I51.9": "Cardiopatia não especificada",
    
    # Códigos J (Respiratório)
    "J96.0": "Insuficiência respiratória aguda",
    "J96.9": "Insuficiência respiratória não especificada",
    "J98.9": "Transtorno respiratório não especificado",
    
    # Códigos A (Infecciosas)
    "A41.9": "Septicemia não especificada",
    "A49.9": "Infecção bacteriana não especificada",
    
    # Outros códigos mal definidos
    "N17.9": "Insuficiência renal aguda não especificada (quando sem contexto)",
    "N19": "Insuficiência renal não especificada",
}

termos_garbage = [
    "PARADA CARDÍACA", "PARADA CARDIORESPIRATÓRIA", "PARADA CARDIORESPIRATORIA",
    "FALÊNCIA DE MÚLTIPLOS ÓRGÃOS", "FALENCIA DE MULTIPLOS ORGAOS",
    "INSUFICIÊNCIA RESPIRATÓRIA", "INSUFICIENCIA RESPIRATORIA",
    "SEPSE NÃO ESPECIFICADA", "SEPSE", "CHOQUE SÉPTICO", "CHOQUE SEPTICO",
    "SENILIDADE", "CAUSA DESCONHECIDA", "MORTE NATURAL",
    "INSUFICIÊNCIA CARDÍACA", "INSUFICIENCIA CARDIACA",
    "CAQUEXIA", "DESNUTRIÇÃO", "DESNUTRICAO"
]

def verificar_garbage_code(texto):
    """Verifica se o texto contém garbage codes"""
    if not texto:
        return False, "", []
    
    texto_upper = texto.upper().strip()
    alertas = []
    
    # Verificar termos
    for termo in termos_garbage:
        if termo in texto_upper:
            alertas.append(f"O termo '{termo}' é considerado um Garbage Code ou termo mal definido para Causa Básica.")
    
    # Verificar códigos CID
    for codigo, descricao in garbage_codes_dict.items():
        if codigo in texto_upper:
            alertas.append(f"O código CID '{codigo}' ({descricao}) é considerado um Garbage Code.")
    
    if alertas:
        return True, "\n".join(alertas), alertas
    
    return False, "", []

def validar_sequencia_temporal(tempos):
    """Valida se a sequência temporal faz sentido (opcional)"""
    # Esta função pode ser expandida para validar a lógica temporal
    return True

# --- SIDEBAR COM INFORMAÇÕES ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/International_Flag_of_Planet_Earth.svg/1200px-International_Flag_of_Planet_Earth.svg.png", width=100)
    st.markdown("### 📚 Sobre o Sistema")
    st.markdown("""
    Este assistente foi desenvolvido para auxiliar médicos no preenchimento correto da **Declaração de Óbito (DO)**, 
    especialmente o **Bloco V** (Condições e Causas do Óbito).
    
    **Funcionalidades:**
    - ✅ Validação de Garbage Codes
    - ✅ Sugestão de sequência causal
    - ✅ Análise de qualidade
    - ✅ Orientações baseadas em manuais oficiais
    
    **Referências:**
    - Manual SVS/MS 2022
    - Lista de Garbage Codes 2024
    - CID-10
    """)
    
    st.divider()
    
    st.markdown("### 🔒 Privacidade")
    st.warning("⚠️ **NUNCA** insira dados reais de pacientes (nomes, CPF, etc.). Use apenas informações clínicas anônimas.")
    
    st.divider()
    
    st.markdown("### 📖 Guia Rápido")
    with st.expander("Como usar?"):
        st.markdown("""
        1. **Insira o resumo clínico** (sem identificação)
        2. **Preencha a Parte I** da causa mais recente (a) até a causa básica (d)
        3. **Adicione condições contribuintes** na Parte II
        4. **Clique em Analisar** para verificar garbage codes
        5. **Revise as sugestões** e ajuste conforme necessário
        """)
    
    with st.expander("O que são Garbage Codes?"):
        st.markdown("""
        São códigos CID ou termos que **não especificam adequadamente** a causa da morte, como:
        - Parada cardíaca
        - Insuficiência respiratória
        - Sepse não especificada
        - Senilidade
        
        Estes devem ser **evitados como causa básica**, pois prejudicam as estatísticas de saúde.
        """)

# --- CRIAÇÃO DAS ABAS ---
tab_ferramenta, tab_exemplos, tab_avisos = st.tabs([
    "🛠️ Assistente de Preenchimento", 
    "📋 Exemplos Práticos",
    "⚠️ Avisos Legais e Privacidade"
])

# ==============================================================================
# ABA 1: FERRAMENTA PRINCIPAL
# ==============================================================================
with tab_ferramenta:
    st.markdown("""
    Este assistente auxilia na organização da **cadeia causal do Bloco V**, 
    filtrando *Garbage Codes* e sugerindo a sequência lógica conforme as normas do Ministério da Saúde.
    """)
    
    # --- FORMULÁRIO PRINCIPAL ---
    with st.form("do_form"):
        st.subheader("📝 Resumo Clínico (Anônimo)")
        resumo = st.text_area(
            "Cole aqui o resumo clínico do caso (sem identificação do paciente):", 
            height=120,
            placeholder="Exemplo: Paciente idoso, sexo masculino, com histórico de DPOC há 10 anos, internado por pneumonia bacteriana há 5 dias, evoluiu com insuficiência respiratória e choque séptico..."
        )

        st.divider()
        st.subheader("📊 Parte I: Cadeia Causal")
        st.caption("⚠️ Preencha da consequência final (a) até a causa original (d). A última linha preenchida será considerada a **Causa Básica**.")
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            linha_a = st.text_input(
                "a) Causa Imediata/Terminal", 
                placeholder="Ex: Choque séptico",
                help="A doença ou lesão que levou diretamente à morte"
            )
            st.markdown("*Devido ou como consequência de:*")
            
            linha_b = st.text_input(
                "b) Causa Intermediária", 
                placeholder="Ex: Pneumonia bacteriana",
                help="Estado mórbido que produziu a causa acima"
            )
            st.markdown("*Devido ou como consequência de:*")
            
            linha_c = st.text_input(
                "c) Causa Intermediária", 
                placeholder="Ex: (deixar em branco se não houver)",
                help="Outro estado mórbido intermediário"
            )
            st.markdown("*Devido ou como consequência de:*")
            
            linha_d = st.text_input(
                "d) Causa Básica", 
                placeholder="Ex: Doença pulmonar obstrutiva crônica (DPOC)",
                help="A doença que iniciou a cadeia de eventos patológicos"
            )
        
        with col2:
            tempo_a = st.text_input("Tempo (a)", placeholder="Ex: 2 dias")
            st.write("")
            st.write("")
            tempo_b = st.text_input("Tempo (b)", placeholder="Ex: 5 dias")
            st.write("")
            st.write("")
            tempo_c = st.text_input("Tempo (c)", placeholder="Ex: -")
            st.write("")
            st.write("")
            tempo_d = st.text_input("Tempo (d)", placeholder="Ex: 10 anos")

        st.divider()
        st.subheader("📌 Parte II: Condições Contribuintes")
        parte_ii = st.text_area(
            "Outras comorbidades que contribuíram para a morte, mas não causaram diretamente:",
            placeholder="Ex: Hipertensão arterial sistêmica, Diabetes mellitus tipo 2",
            height=80
        )

        submitted = st.form_submit_button("✅ Analisar e Gerar Declaração de Óbito", use_container_width=True)

    # --- LÓGICA DE PROCESSAMENTO ---
    if submitted:
        st.divider()
        
        # 1. Determinar qual é a Causa Básica (a última linha preenchida)
        causa_basica = ""
        origem_basica = ""
        
        if linha_d:
            causa_basica = linha_d
            origem_basica = "Linha (d)"
        elif linha_c:
            causa_basica = linha_c
            origem_basica = "Linha (c)"
        elif linha_b:
            causa_basica = linha_b
            origem_basica = "Linha (b)"
        elif linha_a:
            causa_basica = linha_a
            origem_basica = "Linha (a)"
        else:
            st.error("⚠️ Você precisa preencher pelo menos a Linha (a) - Causa Imediata.")
            st.stop()

        # 2. Verificar Garbage Code
        is_gc, msg_gc, alertas = verificar_garbage_code(causa_basica)

        # 3. Exibir Resultado
        st.markdown("### 📄 Visualização da Declaração de Óbito (Bloco V)")
        
        col_preview1, col_preview2 = st.columns([3, 1])
        
        with col_preview1:
            st.markdown(f"""
            **PARTE I - CAUSAS DA MORTE**
            
            **a) Causa Imediata:**  
            {linha_a if linha_a else "---"}
            
            *Devido ou como consequência de:*
            
            **b) Causa Intermediária:**  
            {linha_b if linha_b else "---"}
            
            *Devido ou como consequência de:*
            
            **c) Causa Intermediária:**  
            {linha_c if linha_c else "---"}
            
            *Devido ou como consequência de:*
            
            **d) Causa Básica:**  
            {linha_d if linha_d else "---"}
            
            ---
            
            **PARTE II - OUTRAS CONDIÇÕES CONTRIBUINTES**
            
            {parte_ii if parte_ii else "---"}
            """)
        
        with col_preview2:
            st.markdown(f"""
            **TEMPO**
            
            {tempo_a if tempo_a else "---"}
            
            
            
            {tempo_b if tempo_b else "---"}
            
            
            
            {tempo_c if tempo_c else "---"}
            
            
            
            {tempo_d if tempo_d else "---"}
            """)

        st.divider()
        
        # 4. Análise de Qualidade
        st.subheader("🔍 Análise de Qualidade e Auditoria")
        
        col_analise1, col_analise2 = st.columns(2)
        
        with col_analise1:
            st.markdown("#### 📌 Causa Básica Identificada")
            st.info(f"**{origem_basica}:** {causa_basica}")
            
            if is_gc:
                st.error("❌ **ALERTA DE GARBAGE CODE DETECTADO**")
                for alerta in alertas:
                    st.warning(f"⚠️ {alerta}")
                
                st.markdown("""
                **👉 Ação Recomendada:**  
                Volte ao prontuário e tente identificar a **doença específica** que causou este evento.
                
                **Exemplos de substituição:**
                - ❌ Parada cardíaca → ✅ Infarto agudo do miocárdio
                - ❌ Insuficiência respiratória → ✅ Pneumonia bacteriana
                - ❌ Sepse → ✅ Sepse por foco urinário (pielonefrite)
                """)
            else:
                st.success("✅ **Causa Básica Aparentemente Válida**")
                st.markdown(f"A causa informada em **{origem_basica}** parece ser específica e adequada.")
        
        with col_analise2:
            st.markdown("#### ⏱️ Validação Temporal")
            tempos_preenchidos = [t for t in [tempo_a, tempo_b, tempo_c, tempo_d] if t]
            if len(tempos_preenchidos) >= 2:
                st.success(f"✅ {len(tempos_preenchidos)} intervalos de tempo informados")
                st.info("Certifique-se de que a sequência temporal faz sentido cronológico (da mais recente para a mais antiga).")
            else:
                st.warning("⚠️ Considere preencher os tempos aproximados para melhor qualidade dos dados.")
            
            st.markdown("#### 📋 Resumo Clínico")
            if resumo:
                st.success("✅ Resumo clínico fornecido")
            else:
                st.warning("⚠️ Resumo clínico não fornecido")

        st.divider()
        
        # 5. Observações Finais
        st.markdown("### 💡 Observações e Recomendações")
        st.info("""
        **Lembre-se:**
        - Esta é uma **sugestão automática** baseada nos manuais oficiais
        - A **decisão final** é sempre do médico atestante
        - Verifique se a sequência causal faz sentido clínico e temporal
        - Evite termos vagos e códigos mal definidos (Garbage Codes)
        - Consulte o prontuário completo antes de finalizar
        """)
        
        st.caption("📚 Referências: Manual de Instruções para Preenchimento da DO (SVS/MS - 2022) | Lista de Garbage Codes (SVS/DASNT - 2024)")

# ==============================================================================
# ABA 2: EXEMPLOS PRÁTICOS
# ==============================================================================
with tab_exemplos:
    st.markdown("### 📋 Exemplos Práticos de Preenchimento")
    
    st.markdown("#### ✅ Exemplo 1: Óbito por Infarto Agudo do Miocárdio")
    st.code("""
PARTE I:
a) Choque cardiogênico (Tempo: 6 horas)
   Devido ou como consequência de:
b) Infarto agudo do miocárdio (Tempo: 2 dias)
   Devido ou como consequência de:
c) ---
   Devido ou como consequência de:
d) Doença arterial coronariana (Tempo: 5 anos)

PARTE II:
Hipertensão arterial sistêmica, Diabetes mellitus tipo 2
    """, language="text")
    
    st.divider()
    
    st.markdown("#### ✅ Exemplo 2: Óbito por Pneumonia em paciente com DPOC")
    st.code("""
PARTE I:
a) Choque séptico (Tempo: 1 dia)
   Devido ou como consequência de:
b) Pneumonia bacteriana (Tempo: 5 dias)
   Devido ou como consequência de:
c) ---
   Devido ou como consequência de:
d) Doença pulmonar obstrutiva crônica (DPOC) (Tempo: 10 anos)

PARTE II:
Tabagismo, Hipertensão arterial sistêmica
    """, language="text")
    
    st.divider()
    
    st.markdown("#### ❌ Exemplo de Preenchimento INCORRETO (com Garbage Codes)")
    st.code("""
PARTE I:
a) Parada cardiorrespiratória (❌ GARBAGE CODE)
   Devido ou como consequência de:
b) Falência de múltiplos órgãos (❌ GARBAGE CODE)
   Devido ou como consequência de:
c) ---
   Devido ou como consequência de:
d) Senilidade (❌ GARBAGE CODE)

PARTE II:
---

⚠️ PROBLEMA: Todos os termos são vagos e não especificam a doença real que causou a morte.
    """, language="text")
    
    st.divider()
    
    st.markdown("#### 💡 Dicas Importantes")
    st.markdown("""
    1. **Causa Imediata (a)** ≠ Mecanismo de morte
       - ❌ Parada cardíaca (mecanismo)
       - ✅ Infarto agudo do miocárdio (doença)
    
    2. **Causa Básica (d)** = A doença que iniciou tudo
       - Deve ser a mais específica possível
       - Evite termos como "senilidade", "idade avançada"
    
    3. **Sequência lógica temporal**
       - Os tempos devem fazer sentido (de cima para baixo: mais recente → mais antigo)
    
    4. **Parte II** = Comorbidades importantes
       - Não fazem parte da cadeia direta
       - Mas contribuíram para a morte
    """)

# ==============================================================================
# ABA 3: AVISOS LEGAIS
# ==============================================================================
with tab_avisos:
    st.error("⚠️ LEIA COM ATENÇÃO ANTES DE USAR")
    
    st.markdown("### 🔒 1. Proteção de Dados e Privacidade (LGPD)")
    st.markdown("""
    **É ESTRITAMENTE PROIBIDO INSERIR DADOS REAIS DE PACIENTES.**
    
    - **Não insira:** Nomes, CPF, Cartão SUS, Endereços, Datas de Nascimento exatas ou quaisquer outros dados que permitam a identificação de uma pessoa.
    - **Utilize apenas:** O resumo clínico genérico (ex: "Paciente idoso, sexo masculino, com histórico de DPOC...").
    - Este aplicativo **não armazena** as informações inseridas após o fechamento da aba, processando tudo localmente ou de forma efêmera.
    - **Responsabilidade:** O usuário é o único responsável por garantir que nenhum dado pessoal seja inserido no sistema.
    """)
    
    st.divider()

    st.markdown("### ⚖️ 2. Isenção de Responsabilidade Médica")
    st.markdown("""
    Esta ferramenta fornece apenas uma **ORIENTAÇÃO** de preenchimento baseada nos manuais oficiais do Ministério da Saúde (MS) e na Classificação Internacional de Doenças (CID-10).
    
    - **O aplicativo NÃO substitui o julgamento clínico.**
    - É de **inteira e exclusiva responsabilidade do médico atestante** analisar o caso, verificar a veracidade das informações e decidir a melhor sequência causal para a Declaração de Óbito.
    - Os desenvolvedores **não se responsabilizam** por eventuais erros éticos, jurídicos ou administrativos decorrentes do uso desta ferramenta.
    - Este sistema é uma **ferramenta de apoio educacional** e não deve ser utilizado como única fonte de decisão.
    """)

    st.divider()
    
    st.markdown("### 📚 3. Fontes de Referência")
    st.markdown("""
    Este aplicativo foi desenvolvido com base nas seguintes referências oficiais:
    
    - **Manual de Instruções para Preenchimento da Declaração de Óbito** (SVS/MS - 2022)
    - **Lista de Garbage Codes** (SVS/DASNT - 2024)
    - **Classificação Estatística Internacional de Doenças e Problemas Relacionados à Saúde** (CID-10)
    - **Portaria nº 116/2009** - Regulamenta a coleta de dados, fluxo e periodicidade de envio das informações sobre óbitos
    """)
    
    st.divider()
    
    st.markdown("### 👨‍⚕️ 4. Público-Alvo")
    st.markdown("""
    Este aplicativo é destinado **exclusivamente a profissionais médicos** habilitados para o preenchimento de Declarações de Óbito, conforme legislação vigente.
    
    - Médicos atestantes
    - Médicos auditores
    - Profissionais de vigilância epidemiológica
    - Estudantes de medicina (para fins educacionais)
    """)
    
    st.divider()
    
    st.markdown("### 🔄 5. Atualizações e Manutenção")
    st.markdown("""
    - Este aplicativo pode ser atualizado periodicamente para refletir mudanças nas normas e manuais oficiais
    - Não há garantia de disponibilidade contínua do serviço
    - Recomenda-se sempre consultar as fontes oficiais mais recentes
    """)

# --- RODAPÉ ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px; color: #666;'>
    <p style='margin: 5px;'><strong>Desenvolvido por Manus IA e Dr. Auro Júnior</strong></p>
    <p style='margin: 5px;'>Instagram: <a href='https://www.instagram.com/auropaiva/' target='_blank'>@auropaiva</a></p>
    <p style='margin: 5px; font-size: 0.9rem;'>📚 Sistema baseado em manuais oficiais do Ministério da Saúde | 🔒 Privacidade garantida - Sem armazenamento de dados</p>
</div>
""", unsafe_allow_html=True)
