# Code Snake no fluxo diário existente

Revisão de 27/10/2026. Esta etapa autoriza a integração do gerador no workflow
`update-code-quest.yml` da branch de revisão. A execução com escrita só será
possível após uma decisão separada de integrar o PR na branch padrão.

O agendamento continua `17 8 * * *` (05:17 em Brasília). CODE QUEST faz a única
consulta existente e grava `assets/code-quest/calendar.json`. Barrel Quest e
Code Snake leem esse mesmo arquivo, offline. Não há calendário paralelo,
token, consulta ou cron adicional. O replay Snake é determinístico: entradas
iguais produzem os mesmos quatro SVGs, inclusive as versões estáticas/mobile.

## Arquivos que a rotina pode atualizar

A lista explícita de staging contém exatamente nove caminhos:

1. `assets/code-quest/calendar.json`
2. `assets/code-quest/code-quest.svg`
3. `assets/code-quest/code-quest-static.svg`
4. `assets/arcade/barrel-quest.svg`
5. `assets/arcade/barrel-quest-static.svg`
6. `assets/code-snake/code-snake.svg`
7. `assets/code-snake/code-snake-mobile.svg`
8. `assets/code-snake/code-snake-static.svg`
9. `assets/code-snake/code-snake-static-mobile.svg`

Somente os quatro últimos são escritos pelo gerador Snake. Ele não modifica
o JSON. Os geradores usam substituição por arquivo temporário adjacente
(`*.svg.tmp`; para o JSON, `calendar.json.tmp`), removido ao terminar. Esses
temporários não fazem parte do staging. README, fontes, testes, PNGs de QA,
licenças e documentação não são atualizados automaticamente.

## Segurança e idempotência

O job de teste permanece com `contents: read`, checkout sem credenciais
persistidas e ações fixadas por SHA. Executa a suíte Python e os três
geradores em `--check`. O job de atualização mantém `needs: test`, a condição
que exclui PRs e exige a branch padrão, e `contents: write` somente nesse job.
O token existente continua limitado ao passo CODE QUEST; os outros geradores
não recebem um token adicional. A concorrência e o push normal são mantidos.

No job de atualização, geração dos três conjuntos, checks e testes completos
precedem o staging/commit. Falhas abortam antes de publicar. A escrita local
é atômica por arquivo, não uma transação entre os nove arquivos; se uma etapa
posterior falhar, pode haver arquivos modificados no runner descartável,
mas o passo de commit não executa. Nenhum estado parcial é enviado ao GitHub.
Sem diff, não há commit. Conteúdo idêntico preserva bytes e mtime.

O teste de integração usa calendários sintéticos somente em um diretório
temporário: uma consulta simulada por ciclo, geração/check dos nove arquivos,
troca de calendário denso para vazio, segunda execução idempotente e falha de
entrada preservando as saídas. Socket real é bloqueado durante o teste.
Os testes existentes de falha de rede e entrada inválida continuam na suíte.
O job de escrita na main não foi disparado durante esta revisão.
