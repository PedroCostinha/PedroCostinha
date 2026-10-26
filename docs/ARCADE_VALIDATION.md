# Barrel Quest — evidências do protótipo

Validação local em 26/10/2026, branch `feat/arcade-barrel-quest`, sobre
`062ff0d110b866defea9845f7e35d7b1017ab3c0`. Sem merge, deploy, Pages ou execução
do job de escrita na main. Plano e auditoria: [ARCADE_COLLECTION.md](ARCADE_COLLECTION.md).

## Dados utilizados

Snapshot real já publicado pelo CODE QUEST: **26/10/2025–25/10/2026**, origem
`github-graphql`, 365 dias, 53 semanas, 287 contribuições e 40 dias ativos.
Não foi feita nova consulta GraphQL para o protótipo. Esse snapshot não deve
ser confundido com uma consulta ao vivo no instante da visualização.

SHA-256 de `assets/code-quest/calendar.json`:
`2bef04859c746702bdbd6f129a8abaed78e4e4bc555453b79eff032f3cc6259a`.

Os cinco trechos somam **3 + 8 + 0 + 12 + 264 = 287**. O trecho vazio continua
vazio; não recebe contribuições ou pontos artificiais. A rota é demonstrativa,
com autoria própria, e não tenta simular a criação de atividade no GitHub.

## Verificações executadas

Ambiente: Windows, Python **3.12.14**, Node **24.22.1**, Chrome **155.0.8059.85**
em modo headless. Dependências de QA disponíveis no runtime local; a geração
e os testes de CI continuam usando somente a biblioteca padrão de Python.

| Verificação | Resultado |
| --- | --- |
| `python -m unittest discover -s tests -v` | **42 testes aprovados**; 32 existentes + 10 novos; 16,889 s na rodada final |
| `python scripts/generate_code_quest.py --check` | V2 válida: 365 dias, 53 semanas, 287 contribuições; 220.758 bytes |
| `python scripts/generate_arcade.py --check` | Ambos os SVGs válidos e reproduzíveis do mesmo snapshot |
| SVG animado | 117.199 bytes; viewBox 1200×650; abaixo de 250 kB |
| SVG estático | 51.182 bytes; sem keyframes e sem declarações de animação |
| Geração repetida | `Unchanged`; testes confirmam mtime preservado para conteúdo idêntico |
| Entrada inválida | Falha antes de escrever; artefatos anteriores e calendário preservados |
| Segurança SVG | XML, IDs únicos, referências internas, metadados e cinco trechos validados; scripts, imagens, handlers, estilos inline e recursos externos rejeitados |
| Geometria | Barris seguem declives; cinco encontros e saltos; rota contínua, quatro escadas; 6.401 amostras de colisão do sprite completo com barris e tetos |
| CODE QUEST preservado | `git diff --exit-code origin/main --` em módulos, gerador, testes, documentos e assets; bloco marcado do README comparado integralmente |
| `git diff --check` | Sem erros de whitespace |

O script `node scripts/preview_arcade.cjs` verifica poses e placar únicos,
posição de salto/subida, fade no início e reinício, ausência de animações em
movimento reduzido e seleção real de `<picture>`. Uma página local serve os
SVGs como imagens; também é verificado que o conteúdo da imagem muda com o
tempo no modo animado e que a largura de 390 px não tem overflow horizontal.
As páginas não registraram erros JavaScript. O código de QA não é incluído no
SVG e não roda dentro do README.

## Revisão visual

![Fotograma de conclusão](../assets/arcade/preview.png)

![Seis fotogramas: entrada, salto, escada, piso central, piso superior e conclusão](arcade/frames.png)

Os fotogramas foram produzidos do SVG real com as timelines CSS pausadas em
1,35; 3,84; 6,10; 15,00; 25,52 e 29,50 segundos, sem alterar os SVGs publicados.
A composição de contato apenas redimensiona essas capturas e adiciona rótulos.
Foi corrigida uma diagonal de fundo que avançava sobre o HUD; o painel foi
ampliado para acomodar o salto no piso superior. Quadros de corrida são distintos.

![Fonte estática selecionada em largura de celular](arcade/mobile-static.png)

Fontes secundárias ficam pequenas no celular; o link para abrir a imagem em
tamanho integral e a alternativa estática permanecem disponíveis no README.

## Limites e passos para aprovação

- O protótipo é uma sequência automática de 32 s, com colisões de uma rota
  previamente calculada. Não é um jogo controlável, nem um motor de física
  completo. Pontuação e terminais dependem dos dados; a rota/cenário são fixos.
- Foi validado no Chrome local. Firefox, Safari, leitores de tela reais e a
  renderização/cache de imagens do GitHub ainda exigem verificação específica.
  Não se afirma compatibilidade universal a partir da sintaxe.
- O workflow foi revisado e seus comandos rodaram localmente. Não foi
  disparado job remoto de atualização/publicação, e nenhum token novo foi criado.
- Os PNGs são evidências deste snapshot, não artefatos atualizados pelo cron.
- Não há links de jogar fictícios. O repositório separado e GitHub Pages são
  uma proposta, a implementar após aprovação de escopo e publicação.
- Pac-Man depende de autorização/licença verificável do código e dos recursos;
  não foi incorporado. Space Defense e Code Snake permanecem planejados.

Próximos passos: revisar a branch e o visual, ampliar a matriz de navegadores
e acessibilidade, aprovar a integração no perfil e então implementar a versão
TypeScript com teclado em repositório próprio. Merge/deploy exigem aprovação.
