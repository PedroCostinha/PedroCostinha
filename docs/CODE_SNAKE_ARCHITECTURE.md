# Code Snake no perfil — proposta de 27/10/2026

Base auditada: `bceb8e1a87ac1ddf3c04d8cc816a0f17a5449868`. Branch local `feat/code-snake-profile`. Protótipo para revisão; sem publicação ou alteração da automação existente.

## Auditoria

CODE QUEST V2: `generate_code_quest.py` consulta GraphQL somente no fluxo normal; `--calendar` reproduz um snapshot e `--check` verifica saídas. `code_quest/data.py` valida calendário; motion/sprites/scene geram SVG/CSS autocontido. Barrel Quest: `generate_arcade.py` lê `assets/code-quest/calendar.json`, valida com o mesmo código e gera dois SVGs sem rede. `scripts/arcade` contém simulação demonstrativa, sprites e composição. Testes são unittest; previews usam Playwright/Chrome e Firefox. Não alterar nenhum desses arquivos.

O workflow `update-code-quest.yml` usa cron existente 08:17 UTC, única consulta e token do job. Testa em PR sem publicar; update apenas na branch padrão gera CODE QUEST, depois Barrel, valida e commita uma allowlist. Nesta etapa o workflow fica intacto; os SVGs novos serão snapshots locais. Após aprovação, adicionar geração e check ao mesmo job e seus caminhos à allowlist, depois de gravado o calendário. Nunca criar outro fetch/cron/token.

O perfil não possui mapa de licença próprio. O novo pacote terá MIT explícita para algoritmos e testes e direitos reservados para sprite/paleta/composição/SVGs, sem relicenciar os trabalhos existentes. Inventário em `CODE_SNAKE_LICENSING.md`.

## Dados e arquitetura

Novo pacote isolado `scripts/code_snake/{model,scene,art}.py`, CLI `generate_code_snake.py` e testes `test_code_snake.py`. Importar apenas o validador existente e reutilizar o escritor atômico. Receber exatamente o calendário existente, sem gravá-lo ou copiá-lo. Determinismo byte a byte, sem timestamp de execução. CLI valida todos os outputs antes de escrever; --check detecta drift.

Para jogos seguintes, propor um registro declarativo de demos com id, função de renderização, saídas desktop/mobile/estáticas e orçamento. Cada demo recebe o mesmo Calendar validado em memória; o registro não possui provedor de rede. Adotar esse registro depois da revisão dos protótipos, sem mover os módulos CODE QUEST ou Barrel nesta etapa. A coleta de contribuições continua sob responsabilidade exclusiva do produtor atual.

Modelo calcula rota serpentina ortogonal em semanas recentes, estados de segmentos, itens em dias ativos, datas e contagens coletadas; a contagem mostrada é soma exata dos dias visitados, nunca pontos inventados. Exibir separadamente total anual e amostra coletada. Dias do ano inteiro permanecem no calendário inferior e nos metadados, incluindo zeros e semanas parciais. Formatos mobile e desktop podem ter recortes diferentes explicitamente rotulados; a fonte e total anual são idênticos.

Arte original: Nib, cobrinha robótica modular, cabeça quadrada com visor de dois pixels claros, antena e placas vermelhas; corpo de módulos grafite com realces. Itens são núcleos de dados em losango. Nada derivado de sprites ou código de outras franquias. Preto/grafite/vermelho, pixel art, movimento interpolado CSS linear pelas células; crescimento em coletas; loop de 18 s com breve conclusão e fade de retorno. Estático mostra pose legível, total e percurso sem keyframes. Preferência reduzida também funciona dentro do SVG animado. Não depender de JS no README.

Saídas em `assets/code-snake/`: code-snake.svg, code-snake-static.svg e variantes -mobile. `picture` seleciona estático antes de mobile quando movimento reduzido. Uma tabela com duas demos visíveis tira Barrel do bloco recolhido e apresenta Code Snake em desenvolvimento. Apenas a documentação vai para details. CODE QUEST fica byte a byte preservado. Nenhum link “Jogar Code Snake” até publicação e validação da versão interativa.

## Planos separados

1. Demo: validar gerador, calendário real/zerado/denso, rota sem colisão, itens/growth/contador sincronizados, budget, referências internas, determinismo, estático e imagem em Chrome/Firefox. Revisão humana da vitrine e cache/renderização GitHub antes de integrar a automação.
2. Jogo: repositório `arcade-collection`, branch `feat/code-snake-playable`, TypeScript/Canvas e pontuação própria; build de revisão isolado em prototype-dist, rota `/code-snake/`. Manter Barrel 1.1.0 e raiz. Sem calendário no runtime, sem deploy. Documento completo e plano da home: `arcade-collection/docs/CODE_SNAKE_ARCHITECTURE.md` no checkout irmão.
3. Home: mockup local `/collection/`, catálogo com versões/disponibilidade; integração futura primeiro em subrota, mantendo Barrel na raiz. Promoção ao Pages e links somente com aprovação.

Riscos: escala do calendário em 320 px, compatibilidade de animação em img no GitHub, cache do snapshot, acessibilidade e tamanho de arquivos. Prévia local não certifica GitHub, hardware móvel, Safari ou leitor de tela. Não modificar CODE QUEST V2, Barrel, workflows ou Release. Relatório factual dos testes em `CODE_SNAKE_VALIDATION.md`.
