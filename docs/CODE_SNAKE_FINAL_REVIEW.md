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

## GitHub real: antes e depois

Chrome 155.0.8059.85 e Firefox 153.0 executados, ambos sem overflow ou erros
de página. Antes: commit `bed2270`; depois: commit funcional `0ffa30d`.
As capturas são do README real dessas revisões, sem substituir HTML/CSS,
e não da página do perfil publicada pela main. O commit de evidências
mantém exatamente o mesmo README e os mesmos SVGs do commit funcional.

Dimensões aproximadas no Chrome; no Firefox as diferenças são inferiores
a 0,1 px. A largura útil do README é menor que a viewport por causa da
interface do próprio GitHub.

| Viewport | Barrel antes → depois | Snake antes → depois |
| --- | --- | --- |
| 320 px | 60×33 → 254×138 | 139×171 → 254×312 |
| 390 px | 98×53 → 324×176 | 171×210 → 324×398 |
| 768 px | 142×77 → 406×220 | 209×124 → 406×241 |
| 1440 px | 376×204 → 838×454 | 407×241 → 838×497 |

Resultados estruturados: [antes Chrome](code-snake-final/before/chrome/results.json),
[depois Chrome](code-snake-final/after/chrome/results.json),
[antes Firefox](code-snake-final/before/firefox/results.json) e
[depois Firefox](code-snake-final/after/firefox/results.json).
Capturas reais em 390 px: [antes](code-snake-final/before/chrome/github-390-showcase.png)
e [depois](code-snake-final/after/chrome/github-390-showcase.png).
Desktop: [antes](code-snake-final/before/chrome/github-1440-showcase.png) e
[depois](code-snake-final/after/chrome/github-1440-showcase.png).
As pastas também contêm 320/768 px e as capturas Firefox.

Os dois jogos animaram como `img` sem clique ou expansão. Todos os recursos
estáticos selecionados depois foram baixados e comparados byte a byte com
os SVGs locais, sem keyframes. Firefox produziu pares de pixels idênticos;
Chrome teve variação residual de rasterização (máximo de 18 níveis em um
canal; maior média absoluta de 0,001161 em escala 0–255). O comparador exige
bytes SVG exatos, delta máximo ≤32, até 3% dos canais e média ≤0,03. Os JSONs
registram cada comparação. As capturas documentais aguardam o fade inicial
com a imagem visível; SVGs fora da viewport podem adiar seu relógio de pintura.
Nenhum SVG foi alterado para corrigir diferenças do capturador.

As demos locais Snake e Barrel também passaram em ambos os navegadores:
fontes animadas/estáticas, reset oculto, redução de movimento, espaçamento,
poses, saltos, escadas e placares. Suíte completa: 49/49; três `--check`
aprovados. [CI do commit funcional](https://github.com/PedroCostinha/PedroCostinha/actions/runs/40517297851):
teste aprovado e job de atualização ignorado no PR. Conferir os checks do
head final no PR após o commit de evidências.

Parecer visual: a composição vertical elimina a distribuição desigual e o
espaço vazio da tabela. Ambos os cenários ganham presença e os personagens
ficam mais reconhecíveis. A apresentação segue compacta dentro de cada demo;
textos internos secundários do Barrel continuam pequenos em 320/390 px,
limite do SVG original preservado. A página fica mais alta para dar espaço
às duas imagens, sem duplicá-las ou exigir interação para animar.

Safari, celular físico e leitor de tela real permanecem pendentes. Licenças
e avisos anteriores foram preservados; o novo script de QA integra o escopo
MIT do código, e capturas/arte permanecem reservadas a PedroCostinha.
Esta etapa não aprova merge ou publicação do perfil.
