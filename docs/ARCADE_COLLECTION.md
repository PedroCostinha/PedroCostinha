# ARCADE COLLECTION — estado atual e auditoria

**Barrel Quest 1.1.0 está jogável no [GitHub Pages](https://pedrocostinha.github.io/arcade-collection/).**
O [repositório do jogo](https://github.com/PedroCostinha/arcade-collection) é separado
do perfil; o commit publicado e validado é
[`ffc56b1b312bf91889999902398ebe2fa9b74bee`](https://github.com/PedroCostinha/arcade-collection/commit/ffc56b1b312bf91889999902398ebe2fa9b74bee).

A animação SVG do perfil continua demonstrativa, com placar derivado das
contribuições reais do calendário. A versão interativa tem controles e
pontuação própria da partida, sem relação com commits ou contribuições.

A auditoria abaixo preserva o histórico do protótipo SVG de 26/10/2026,
base `062ff0d110b866defea9845f7e35d7b1017ab3c0`, branch original
`feat/arcade-barrel-quest`. Propostas descritas como parte daquela auditoria
não representam mudanças adicionais de geradores, SVGs ou automações nesta
atualização de divulgação do jogo.

## Perfil e CODE QUEST V2

O README mantém banner responsivo, apresentação técnica, projetos, CODE QUEST e
contato. Preto/grafite e vermelho são a identidade visual. O CODE QUEST tem
calendário completo, sprites originais, saltos, moedas, destaque semanal,
contador sincronizado, reinício com fade e fonte estática em `<picture>`.

Os módulos `data`, `motion`, `sprites`, `scene`, o gerador e os testes existentes
permanecem intactos. `assets/code-quest/calendar.json` já contém os únicos dados
necessários: login, origem, datas consecutivas, contagens e níveis reais.
Reutilizamos seu validador e o escritor determinístico; não é necessário mover
esses módulos para uma biblioteca comum durante um protótipo.

O workflow usa SHAs fixos, permissões de leitura no teste e escrita só no job de
atualização da branch padrão; PRs não publicam. Há timeout, concorrência,
tentativas limitadas de rede, validação antes do commit e push sem force.
Credenciais persistidas no checkout do job de publicação permitem seu push;
o checkout dos testes não as persiste. Não ampliar permissões nem usar PAT.

A integração do protótipo SVG já acrescentou geração/verificação dos dois SVGs
ao mesmo workflow e incluiu esses caminhos no commit condicional existente.
Esta atualização do README não modifica essa integração, seu horário ou suas
permissões. O protótipo reproduz o snapshot salvo; não afirma ser uma consulta
em tempo real. Não há novo cron, consulta, token ou cópia do JSON.

## Referência Pac-Man e autorização

Referência examinada no commit
[`7332e1de7903ab780c3692a4127a59cc13872daa`](https://github.com/abozanona/pacman-contribution-graph/tree/7332e1de7903ab780c3692a4127a59cc13872daa).

- `src/shared/arcade-renderer.ts`: registro de jogos e fábrica de renderizadores.
- `src/shared/providers/`: provedores GitHub, GitLab e cenários sintéticos.
- `github-contributions.ts`: com token, GraphQL e níveis reais; sem token,
  busca commits públicos e recalcula níveis. Essa alternativa não equivale ao
  calendário de contribuições e não será adotada aqui.
- `src/pacman/core/game.ts`: grade, simulação limitada a 3.000 quadros, colisões,
  snapshots do estado e eventos de células.
- `src/pacman/renderers/svg.ts`: exporta histórico em animações SMIL, comprime
  valores repetidos e usa símbolos/imagens de fantasmas definidos nas constantes.
  O arquivo inclui timestamps, que impediriam comparação byte a byte entre
  duas gerações idênticas sem adaptação.
- `action.yml`: execução Node 24; jogos selecionáveis e token do job. A action
  consulta seu próprio provedor, portanto não é um encaixe direto no nosso JSON.

Na árvore completa desse commit não há `LICENSE`, `COPYING` ou `NOTICE`; o
`package.json` (5.3.2) não declara `license` e a API do repositório retorna
`license: null`. O README não fornece uma concessão de licença. Não encontramos
autorização documentada para incorporar código, sprites ou bundle. Não instalamos,
copiamos ou executamos a biblioteca no perfil. Disponibilidade pública e exemplos
de instalação não bastam para presumir permissão de redistribuição.
Ver [orientação do GitHub sobre licenças](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository).

Pac-Man fica condicionado a licença explícita/autorização verificável, revisão
separada da procedência das imagens e permissão para marcas/personagens.
Se autorizado: fixar versão/SHA e integridade, guardar avisos exigidos, testar um
adaptador que receba o snapshot comum e desabilitar consultas próprias e cenários.
Não executar uma action de terceiros com escrita e token só para obter uma prévia.
Nenhum contato foi enviado ao mantenedor.

## Barrel Quest: protótipo original

Ember-7 é um robô entregador com visor e chassis vermelho. Cenário industrial,
barris, robô e poses são vetores desenhados no código deste protótipo. O alfabeto
vetorial já criado para CODE QUEST é reutilizado como recurso próprio do perfil.
Não são usados personagens, sprites, sons ou logotipos da Nintendo.

Cinco plataformas inclinadas e quatro escadas formam uma rota demonstrativa.
O modelo calcula caminhada, corrida, salto e subida; os SVGs usam somente CSS,
formas e referências internas. Barris seguem as rampas e caem nas extremidades.
O reinício fica oculto pelo fade da camada móvel; fundo e dados não piscam.
Na revisão final, o aviso de conclusão foi colocado dentro de um grupo próprio,
evitando que sua timeline CSS sobrescreva o fade. Um teste de regressão e a QA
em Chrome/Firefox verificam o desaparecimento do aviso junto com a camada móvel.

Os dias são divididos em cinco trechos cronológicos contíguos, sem descartar
dias de semanas parciais. Cada terminal de piso entrega a soma de contribuições
desse trecho. O placar cresce nesses encontros e termina exatamente no total
do snapshot. Trechos zerados não dão pontos. Isso é pontuação demonstrativa,
não uma alegação de que jogar criou commits. As contagens não são multiplicadas.
O HUD mostra intervalo, origem, total e dias ativos, sem duplicar o calendário.

O SVG estático mantém o resumo e o placar final sem keyframes. O SVG animado
também atende `prefers-reduced-motion`; o `<picture>` seleciona explicitamente a
fonte estática. Não há JavaScript em Markdown. A largura se adapta ao contêiner;
rótulos pequenos podem exigir ampliação no celular. Link estático sempre visível.

## Coleção e experiência jogável

| Jogo | Situação | Integração / próximo passo |
| --- | --- | --- |
| Pac-Man | Pendente de autorização e revisão dos recursos | Adaptador para snapshot comum, sem novo fetch |
| Barrel Quest | SVG demonstrativo no perfil e versão interativa 1.1.0 publicada | [Jogar](https://pedrocostinha.github.io/arcade-collection/) · [Código](https://github.com/PedroCostinha/arcade-collection) |
| Space Defense | Planejado, arte original | Formação de alvos por trechos de atividade; evitar personagens de franquias |
| Code Snake | Planejado, implementação original | Rota sobre dias reais; manter datas e zero atividade |

O README preserva o bloco CODE QUEST e a animação Barrel Quest expansível.
O link **🎮 JOGAR BARREL QUEST** permanece fora do `<details>`, visível também
com a animação recolhida. Jogos futuros só recebem links quando houver
destinos reais; suas situações na tabela não foram alteradas nesta etapa.

O repositório `PedroCostinha/arcade-collection` já contém a versão interativa:
TypeScript, Canvas 2D, simulação de passo fixo, setas/WASD, Espaço, pausa e
reinício. O jogo foi publicado em GitHub Pages e validado na URL real em
Chrome e Firefox, inclusive com missão completa e layout móvel emulado.
Safari, celular físico e leitor de tela continuam pendentes; a publicação
não equivale a aprovação dessas plataformas.

O perfil continua produzindo o snapshot usado pelas suas animações SVG.
O Barrel Quest interativo é independente desse calendário: suas cinco cargas,
barris, vidas e pontos pertencem à partida. Não consulta contribuições,
GraphQL ou serviços externos em runtime e não exige backend ou token pessoal.
Seu repositório contém os avisos de licenciamento e o workflow oficial Pages.
Esta atualização não altera esse repositório nem dispara outro deploy.

## Critérios de aceite e reprodução

```sh
python -m unittest discover -s tests -v
python scripts/generate_code_quest.py --check
python scripts/generate_arcade.py --check
python scripts/generate_arcade.py
```

O último comando lê somente o JSON existente e escreve só arquivos alterados.
`assets/arcade/preview.png` e os PNGs em `docs/arcade/` são evidências de uma
revisão manual datada; não participam da atualização diária nem aparecem como
dados atuais no README. A QA opcional usa `node scripts/preview_arcade.cjs`,
com Playwright, Sharp e Chrome disponíveis no ambiente de desenvolvimento.
`ARCADE_BROWSER=firefox` seleciona o Firefox instalado pelo Playwright.
`node scripts/review_arcade_github.cjs` verifica o README na interface real
do GitHub, na branch ou no commit de revisão, sem testar o perfil da main.
Antes de aprovar: preservar bytes dos arquivos CODE QUEST, conferir XML,
referências, ausência de recursos externos/scripts, orçamento, proveniência,
pontuação exata, rampas/escadas/saltos, animação em imagem, reinício, fonte
estática e largura móvel. Resultados efetivos e limites são registrados em
`ARCADE_VALIDATION.md`; compatibilidade não é presumida apenas pela sintaxe.
