# Code Snake — revisão final do perfil

27/10/2026. Complementa os relatórios históricos de validação. Base desta
etapa: `bed2270f4e63152e3e636da41af78caa64a1a2b5`.

## Composição e preservação

A tabela foi substituída por duas demonstrações verticais, cada uma com
título, imagem de largura 1200 limitada pelo próprio GitHub e indicação de
disponibilidade. Não há CSS externo nem regras responsivas injetadas no
README. As duas imagens ficam fora de `details`; não exigem interação para
animar. Somente a explicação adicional continua recolhida.

Os `picture` mantêm fontes estáticas para movimento reduzido. Snake mantém
a seleção mobile até 600 px, inclusive a variante estática. Não foi criado
link público para um jogo Snake ainda não hospedado. O link Barrel existente
continua apontando para a versão 1.1.0 aprovada.

Os SVGs originais Barrel e CODE QUEST V2, seus geradores, fontes e testes
foram preservados. Todos os quatro SVGs Snake e o calendário real também
permanecem iguais à base: 366 dias, 53 semanas e 319 contribuições.
O bloco marcado CODE QUEST do README foi comparado integralmente, com a
normalização de finais de linha do Git no Windows.

## Automação

Integração no job diário existente descrita em
[CODE_SNAKE_AUTOMATION.md](CODE_SNAKE_AUTOMATION.md), com os nove caminhos
permitidos e a diferença entre escrita atômica por arquivo e publicação
condicionada a todos os checks. Não foi executado job de escrita na main.

## Validação

A suíte completa passou com 49 testes, incluindo fluxo compartilhado com
uma única consulta simulada, calendário denso/vazio, check dos nove arquivos,
idempotência de bytes/mtime e preservação em entrada inválida. Os três
geradores passaram em `--check`. As falhas de rede e segurança SVG
continuam cobertas pelos testes anteriores.

O script `scripts/review_code_snake_github.cjs` registra capturas e medidas
do README real no GitHub em 320, 390, 768 e 1440 px. Usa o SHA fornecido em
`ARCADE_REVIEW_REF`; `ARCADE_BROWSER=firefox` troca o motor e
`SNAKE_EVIDENCE_DIR` separa saídas antes/depois. `EXPECT_STACKED=1` exige que
ambas as imagens preencham pelo menos 94% da largura útil, sem tabela e
sem overflow. Não altera o HTML/CSS da página. Confere animação sem interação,
seleção responsiva, movimento reduzido e estabilidade dos pixels estáticos
(tolerância pequena para rasterização, registrada no JSON).

Resultados reais, medidas finais e links de CI serão acrescentados após o
push da branch de revisão. Safari, celular físico e leitor de tela real
permanecem pendentes. Esta etapa não aprova merge ou publicação do perfil.
