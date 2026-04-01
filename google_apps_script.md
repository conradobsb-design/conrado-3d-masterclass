# 🔧 Google Apps Script — Receber Orçamentos do Site

## Passo a Passo Completo

### 1. Crie uma Planilha no Google Sheets

Crie uma planilha com o nome que quiser (ex: "Orçamentos Conrado 3D").

Na **linha 1** (cabeçalho), coloque exatamente estas colunas:

| A | B | C | D | E | F | G | H | I | J | K |
|---|---|---|---|---|---|---|---|---|---|---|
| Timestamp | Tipo de Serviço | Possui Arquivo 3D | Resolução | Qtd Imagens | Tipo de Vídeo | Duração do Vídeo | Prazo | Nome | E-mail | WhatsApp |

---

### 2. Abra o Editor de Scripts

1. Na planilha, vá em **Extensões → Apps Script**
2. **Apague** todo o código que estiver lá
3. **Cole** o código abaixo:

```javascript
function doPost(e) {
  try {
    // Lê o JSON enviado pelo site (Content-Type: text/plain)
    var data = JSON.parse(e.postData.contents);
    
    // Abre a planilha ativa (a mesma do script)
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    
    // Monta a linha com os dados recebidos
    var row = [
      data.timestamp || new Date().toLocaleString('pt-BR'),
      data.serviceType || '',
      data.has3dFile || '',
      data.resolution || '',
      data.imageCount || '',
      data.videoType || '',
      data.videoDuration || '',
      data.deadline || '',
      (data.firstName || '') + ' ' + (data.lastName || ''),
      data.email || '',
      data.whatsapp || '',
    ];
    
    // Adiciona a nova linha na planilha
    sheet.appendRow(row);
    
    // Retorno de sucesso
    return ContentService
      .createTextOutput(JSON.stringify({ status: 'success' }))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (error) {
    // Log do erro para debug
    Logger.log('Erro doPost: ' + error.toString());
    
    return ContentService
      .createTextOutput(JSON.stringify({ status: 'error', message: error.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// Função de teste — rode manualmente para verificar se está funcionando
function testeManual() {
  var mockEvent = {
    postData: {
      contents: JSON.stringify({
        serviceType: 'image',
        has3dFile: 'Sim',
        resolution: 'Padrão (4K)',
        imageCount: '4 a 6',
        videoType: '',
        videoDuration: '',
        deadline: 'Médio (2 a 3 semanas)',
        firstName: 'Teste',
        lastName: 'Manual',
        email: 'teste@exemplo.com',
        whatsapp: '(11) 99999-9999',
        timestamp: new Date().toLocaleString('pt-BR'),
      })
    }
  };
  
  doPost(mockEvent);
  Logger.log('✅ Teste concluído! Verifique a planilha.');
}
```

---

### 3. Salve e Implante (Deploy)

1. Clique em **💾 Salvar** (ou Ctrl+S)
2. Clique em **Implantar → Nova implantação**
3. Em "Tipo", selecione **App da Web**
4. Configure:
   - **Descrição:** Orçamentos Conrado 3D
   - **Executar como:** Eu (seu email)
   - **Quem pode acessar:** **Qualquer pessoa** ⚠️ (OBRIGATÓRIO para funcionar)
5. Clique em **Implantar**
6. **Copie a URL** gerada (começa com `https://script.google.com/macros/s/...`)

---

### 4. Cole a URL no Site

No arquivo `src/App.jsx`, **linha 11**, substitua a URL:

```javascript
const GOOGLE_SHEETS_URL = 'SUA_URL_AQUI';
```

---

### 5. Teste

1. Rode a função `testeManual()` no Apps Script para verificar se a planilha recebe os dados
2. Depois, teste pelo site preenchendo o formulário completo

---

## ⚠️ IMPORTANTE: Ao Atualizar o Script

Se você já tem uma implantação anterior, ao modificar o código:

1. Vá em **Implantar → Gerenciar implantações**
2. Clique no **ícone de lápis** (editar) na implantação existente
3. Em "Versão", selecione **Nova versão**
4. Clique em **Implantar**

> **A URL NÃO muda**, mas o código só é atualizado quando você cria uma **nova versão**.

---

## 🐛 Debug: Dados não chegam?

1. No Apps Script, vá em **Execuções** (menu lateral) para ver os logs
2. Verifique se o script está implantado como "Qualquer pessoa"
3. Certifique-se de que não há erros de permissão
4. Rode `testeManual()` para testar isoladamente
