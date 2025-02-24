import streamlit as st
import pytesseract
from PIL import Image
from spellchecker import SpellChecker
import PyPDF2
import re
import difflib
import string
from deepmultilingualpunctuation import PunctuationModel

st.title("Verificador Ortográfico e de Pontuação")

# Função para destacar a pontuação adicionada (em azul)
def highlight_added_punctuation(original, restored):
    """
    Compara o texto original com o texto restaurado e destaca
    as inserções que são pontuações em azul e negrito.
    """
    s = difflib.SequenceMatcher(None, original, restored)
    highlighted = []
    for tag, i1, i2, j1, j2 in s.get_opcodes():
        if tag == 'equal':
            highlighted.append(restored[j1:j2])
        elif tag in ['insert', 'replace']:
            trecho_inserido = restored[j1:j2]
            # Destaca cada caractere de pontuação inserido
            for ch in trecho_inserido:
                if ch in string.punctuation:
                    highlighted.append(f"<span style='color: blue; font-weight: bold;'>{ch}</span>")
                else:
                    highlighted.append(ch)
        # Para deleções, não adicionamos nada
    return "".join(highlighted)

# Upload do arquivo (PDF, PNG, JPEG)
file = st.file_uploader("Selecione um arquivo (PDF, PNG ou JPEG)", type=["pdf", "png", "jpeg", "jpg"])

if file is not None:
    texto_extraido = ""
    
    # Processa PDF
    if file.type == "application/pdf":
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                texto_extraido += page.extract_text() or ""
        except Exception as e:
            st.error(f"Erro ao processar PDF: {e}")
    
    # Processa imagens (PNG, JPEG)
    elif file.type in ["image/png", "image/jpeg"]:
        try:
            imagem = Image.open(file)
            texto_extraido = pytesseract.image_to_string(imagem, lang='por')
        except Exception as e:
            st.error(f"Erro ao processar a imagem: {e}")
    else:
        st.error("Tipo de arquivo não suportado.")

    if texto_extraido:
        st.subheader("Texto Extraído:")
        st.text_area("", texto_extraido, height=200)

        #############################
        # Verificação Ortográfica
        #############################
        spell = SpellChecker(language='pt')
        # Extrai palavras (somente caracteres alfanuméricos)
        palavras = re.findall(r'\w+', texto_extraido)
        erros = spell.unknown(palavras)
        
        st.subheader("Erros Ortográficos e Sugestões:")
        if erros:
            for palavra in erros:
                correcao = spell.correction(palavra)
                st.markdown(f"- **Erro:** {palavra} ➜ **Sugestão:** <span style='color: red; font-weight: bold;'>{correcao}</span>", unsafe_allow_html=True)
        else:
            st.success("Nenhum erro ortográfico encontrado!")
        
        # Gera texto com as correções ortográficas destacadas em vermelho
        texto_corrigido = texto_extraido
        for erro in erros:
            correcao = spell.correction(erro)
            # Substitui a palavra ignorando caixa alta/baixa
            texto_corrigido = re.sub(r'\b' + re.escape(erro) + r'\b',
                                     f"<span style='color: red; font-weight: bold;'>{correcao}</span>",
                                     texto_corrigido,
                                     flags=re.IGNORECASE)
        
        st.subheader("Texto com Ortografia Corrigida (Sugestão):")
        st.markdown(texto_corrigido, unsafe_allow_html=True)

        #############################
        # Restauração de Pontuação
        #############################
        st.subheader("Restauração de Pontuação")
        model = PunctuationModel()
        texto_pontuado = model.restore_punctuation(texto_extraido)
        
        st.markdown("**Texto com Pontuação Restaurada:**", unsafe_allow_html=True)
        st.markdown(texto_pontuado, unsafe_allow_html=True)
        
        # Destaca as pontuações adicionadas em azul
        texto_pontuacao_destacada = highlight_added_punctuation(texto_extraido, texto_pontuado)
        st.markdown("**Destaque das Pontuações Adicionadas (em azul):**", unsafe_allow_html=True)
        st.markdown(texto_pontuacao_destacada, unsafe_allow_html=True)
