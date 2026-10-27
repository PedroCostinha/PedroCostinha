# Code Snake — validação local, 27/10/2026

Branch local `feat/code-snake-profile`, base `bceb8e1a87ac1ddf3c04d8cc816a0f17a5449868`. Sem push, publicação ou alteração do workflow. O README desta branch é uma proposta para revisão.

## Executado

- `python -m unittest discover -s tests -v`: **48/48**, incluindo cinco testes próprios de Code Snake. Regressões CODE QUEST e Barrel passam sem mudar seus fontes.
- Novo gerador e `--check`: quatro SVGs reproduzíveis byte a byte a partir do mesmo snapshot, sem rede. Calendário real de 366 dias, 53 semanas, 319 contribuições, 26/10/2025 a 26/10/2026. Snapshot salvo, não uma consulta de hoje.
- Testes próprios: calendários real, vazio, denso e esparso; rota ortogonal e sem repetição, limites, corpo, itens sobre datas reais ativas, contagens e crescimento sincronizados; preservação de todos os dias/zeros; XML e referências internas; sem scripts/assets externos; preferência reduzida; determinismo e orçamento. CLI não regrava bytes idênticos e preserva saídas se o calendário for inválido. Socket bloqueado nos testes de renderização.
- `generate_code_quest.py --check` e `generate_arcade.py --check`: aprovados. CODE QUEST permanece em 220956 bytes e Barrel em 117214/51197 bytes. Nenhum arquivo existente de gerador, calendário, SVG, teste ou workflow foi alterado. Bloco CODE QUEST do README preservado.
- QA Playwright em Chrome 155.0.8059.85 e Firefox 153.0: SVG muda pixels como img, fontes desktop/mobile corretas, fallback estático fica idêntico entre capturas, reset oculto antes/depois do limite de 18 s, calendário anual completo e redução interna de movimento funcionam. Zero erros de página.
- Tamanhos: animado desktop 182255 bytes; mobile 155780; estático desktop 106678; estático mobile 104323. Limite por saída: 350000 bytes.

Resultados: [Chrome](code-snake/chrome/results.json), [Firefox](code-snake/firefox/results.json), [integridade](code-snake/integrity.json). Prévias: [demo desktop](code-snake/chrome/01-demo-desktop.png), [demo mobile](code-snake/chrome/03-demo-mobile.png), [vitrine](code-snake/chrome/02-showcase-desktop.png), [estático](code-snake/chrome/05-mobile-static.png).

## Revisão visual e limites

As capturas locais foram inspecionadas. A vitrine com duas colunas mantém as demos visíveis e ocupa pouco espaço; no celular seus rótulos internos são pequenos. O Code Snake possui SVG mobile próprio para abrir em largura completa e link estático explícito. Confirmar esse compromisso com o titular; a seleção de picture depende da largura da viewport e a tabela não se reorganiza automaticamente no Markdown do GitHub.

O preview usa um wrapper HTML local com as mesmas tags picture do README; não certifica o sanitizador, o CSS de tabelas nem o cache do GitHub. Essa verificação requer uma branch remota, posteriormente autorizada. Safari, leitor de tela e hardware móvel não testados. O replay é determinístico, não uma inteligência que reage em tempo real, e coleta somente uma amostra rotulada, preservando o total anual separado.

O workflow atual não gera Code Snake: enquanto a integração não for aprovada, seus arquivos são snapshots desta revisão. Atualização futura deve entrar no job existente depois de gravado o mesmo JSON. Não foi criado cron, GraphQL, token, fonte ou calendário paralelo. O README não contém link para jogar Code Snake.

## Reproduzir

Usar Python 3.12+ com biblioteca padrão e executar `python scripts/generate_code_snake.py`, `python scripts/generate_code_snake.py --check` e a suíte unittest. Neste Windows o alias python aponta à Store; foi usado o Python empacotado no runtime do Codex, sem instalar outro Python.

QA opcional: Playwright disponível em NODE_PATH, `node scripts/preview_code_snake.cjs`. `ARCADE_BROWSER=firefox` seleciona Firefox. `node scripts/preview_code_snake.cjs --serve` abre servidor em localhost:4176; `/` mostra vitrine e `/demo` a demo responsiva. Não há código de navegador ou dependências de QA no SVG ou no gerador de produção.

## Revisão visual adicional — 27/10/2026

Na demo mobile, o fim do ciclo aproximava demais “RECORTE CONCLUÍDO” de “ANO COMPLETO”: as caixas de texto se sobrepunham em 1,69 px a 390 px no Chrome. O calendário anual foi deslocado 12 unidades para baixo, sem alterar dimensões, rota, tempos, dados ou arquivos de CODE QUEST/Barrel. Apenas os dois SVGs mobile mudaram. O QA opcional agora verifica um intervalo mínimo de quatro pixels entre essas linhas, no quadro de 16 segundos. Medições após a correção: 8,06 px no Chrome e 6,03 px no Firefox, em 15,001/16/17,999/18,001 segundos. Os 48 testes Python continuam aprovados.

A vitrine de duas colunas é compacta, mas os textos internos dos SVGs ficam pequenos a 390 px; a demo aberta em largura completa é mais legível. A página do jogo mede aproximadamente 1412 px no desktop e 1214 px no celular; os botões iniciais ficam abaixo da primeira tela desktop de 844 px. Esses pontos ficam para decisão visual na revisão, sem redesign nesta correção. A home local cabe em uma tela de 844 px nas duas larguras. Evidências desta etapa foram registradas separadamente das capturas históricas acima. A renderização real da branch no GitHub é uma verificação posterior ao push e não atualiza o perfil da main.
