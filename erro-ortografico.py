import streamlit as st
import pytesseract
from PIL import Image
from spellchecker import SpellChecker
import PyPDF2

st.title("Verificador de Ortografia em Arquivos")

# Permite ao usuário enviar o arquivo
file = st.file_uploader("Selecione um arquivo (PDF, PNG ou JPEG)", type=["pdf", "png", "jpeg", "jpg"])

if file is not None:
    texto_extraido = ""
    
    # Processa arquivos PDF
    if file.type == "application/pdf":
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                texto_extraido += page.extract_text() or ""
        except Exception as e:
            st.error(f"Erro ao processar PDF: {e}")
    
    # Processa arquivos de imagem
    elif file.type in ["image/png", "image/jpeg"]:
        try:
            imagem = Image.open(file)
            # Certifique-se de que o Tesseract esteja instalado e configurado corretamente
            texto_extraido = pytesseract.image_to_string(imagem, lang='por')
        except Exception as e:
            st.error(f"Erro ao processar a imagem: {e}")
    
    else:
        st.error("Tipo de arquivo não suportado.")
    
    if texto_extraido:
        st.subheader("Texto Extraído:")
        st.text_area("", texto_extraido, height=200)
        
        # Verificação ortográfica
        spell = SpellChecker(language='pt')
        palavras = texto_extraido.split()
        erros = spell.unknown(palavras)
        
        st.subheader("Resultado da Verificação Ortográfica:")
        if erros:
            st.error("Foram encontrados erros ortográficos:")
            for palavra in erros:
                st.write(f"- {palavra}")
        else:
            st.success("Nenhum erro ortográfico encontrado!")
