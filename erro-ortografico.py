import streamlit as st
import pytesseract
from PIL import Image
from spellchecker import SpellChecker
import PyPDF2
import re

st.title("Verificador de Ortografia em Arquivos")

# Upload do arquivo (PDF, PNG, JPEG)
file = st.file_uploader("Selecione um arquivo (PDF, PNG ou JPEG)", type=["pdf", "png", "jpeg", "jpg"])

if file is not None:
    texto_extraido = ""
    
    # Processa o arquivo PDF
    if file.type == "application/pdf":
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                texto_extraido += page.extract_text() or ""
        except Exception as e:
            st.error(f"Erro ao processar PDF: {e}")
    
    # Processa arquivos de imagem (PNG, JPEG)
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
        
        # Inicializa o verificador ortográfico para português
        spell = SpellChecker(language='pt')
        
        # Extrai as palavras preservando apenas os caracteres alfanuméricos
        palavras = re.findall(r'\w+', texto_extraido)
        erros = spell.unknown(palavras)
        
        st.subheader("Erros e Sugestões:")
        if erros:
            for palavra in erros:
                correcao = spell.correction(palavra)
                st.markdown(f"- **Erro:** {palavra} ➜ **Sugestão:** <span style='color: red; font-weight: bold;'>{correcao}</span>", unsafe_allow_html=True)
        else:
            st.success("Nenhum erro ortográfico encontrado!")
        
        # Gera uma versão do texto com as correções destacadas em vermelho
        texto_corrigido = texto_extraido
        for erro in erros:
            correcao = spell.correction(erro)
            # Substitui ocorrências exatas ignorando caixa alta/baixa, inserindo a correção em vermelho
            texto_corrigido = re.sub(r'\b' + re.escape(erro) + r'\b',
                                      f"<span style='color: red; font-weight: bold;'>{correcao}</span>",
                                      texto_corrigido,
                                      flags=re.IGNORECASE)
        
        st.subheader("Texto Corrigido (Sugestão):")
        st.markdown(texto_corrigido, unsafe_allow_html=True)
