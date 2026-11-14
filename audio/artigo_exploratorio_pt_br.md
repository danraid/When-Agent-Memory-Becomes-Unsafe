# Quando a memória de agentes se torna insegura: evidências exploratórias sobre substituição temporal de políticas e compactação repetida de contexto

Autor: Daniel Raaid.

Versão narrada em português brasileiro do relatório científico exploratório, de 14 de novembro de 2026. Este material não representa estudo confirmatório, revisão científica independente, artigo aceito ou submissão editorial.

## Resumo

Agentes de inteligência artificial que executam tarefas prolongadas precisam comprimir o histórico de interações. Entretanto, uma memória confiável deve cumprir duas funções distintas: preservar restrições ainda válidas e deixar de aplicar regras legitimamente revogadas ou substituídas. Esta pesquisa apresenta dois estudos exploratórios sintéticos, com respostas reais de modelos GPT, além de uma auditoria do componente original TypeCompact, do trabalho Knowledge Triage, sobre 327 arquivos públicos disponibilizados pelos autores.

No piloto com oito episódios, os métodos de histórico completo, sumarização recursiva e registro externo de políticas acertaram todas as 144 decisões de cada condição. O contexto de janela recente acertou 105 de 144 decisões, aproximadamente 72,9 por cento.

No piloto temporal com quatro episódios, histórico completo, sumarização recursiva, arquivo tipado adaptado e registro externo de políticas acertaram todas as 72 decisões de cada condição. A janela recente acertou 52 de 72 decisões, aproximadamente 72,2 por cento. Todos os métodos acertaram os testes específicos de revogação e de entrada em vigor de novas restrições. Os vinte erros da janela recente ocorreram em casos de controle.

A auditoria de TypeCompact realizou 1.308 medições. Com orçamentos equivalentes a 25, 50, 75 e 100 por cento dos tokens estimados originalmente, foram observados, respectivamente, 19, quatro, um e zero arquivos em condição de compactação inviável.

A conclusão é restrita: os resultados demonstram viabilidade técnica, mas não demonstram superioridade do registro de políticas sobre a sumarização recursiva, nem segurança em ambientes reais. Os testes temporais apresentaram um efeito de teto, com desempenho perfeito das condições estudadas.

## 1. Introdução

Agentes persistentes de inteligência artificial dependem de resumos, memórias recuperadas e estados externos para tomar decisões depois de sequências extensas de eventos. Preservar literalmente uma instrução de segurança pode parecer suficiente. Mas essa estratégia falha conceitualmente quando a própria instrução é revogada, substituída, restringida a um escopo específico ou atualizada por uma autoridade legítima.

Uma proibição antiga que já perdeu validade pode provocar uma rejeição indevida. Em sentido oposto, esquecer uma nova proibição pode provocar a aprovação de uma ação que deveria ser recusada. São erros diferentes e precisam ser medidos separadamente.

Este trabalho dialoga diretamente com pesquisas anteriores. Knowledge Triage, publicado na conferência CIKM de 2026, já estuda a preservação de restrições durante a compactação e apresenta uma arquitetura de retenção tipada. Supersede, divulgado como preprint em 2026, examina a dificuldade de atualizar memórias de agentes. LongMemEval inclui tarefas de atualização de conhecimento, enquanto ACON investiga a otimização de contexto em agentes de longa duração.

Portanto, não reivindicamos como descoberta inédita a simples preservação de restrições nem a existência de memórias desatualizadas. A questão metodológica remanescente envolve autoridade autenticada, validade temporal e comparabilidade das informações oferecidas aos agentes.

O objetivo deste relatório é apresentar o que os experimentos realmente mostraram, incluindo resultados nulos, limitações do instrumento e falhas de revisão automatizada.

## 2. Perguntas de pesquisa

A primeira pergunta é se um fluxo sintético controlado consegue revelar erros de decisão após compactações repetidas do contexto, especialmente erros relativos à substituição de políticas.

A segunda pergunta compara o comportamento de histórico completo, janela recente, resumos recursivos, arquivo tipado adaptado e registro de políticas com versões.

A terceira pergunta examina os limites de viabilidade do componente TypeCompact original quando restrições devem ser preservadas dentro de orçamentos finitos de tokens.

Todas as perguntas são exploratórias. Não houve congelamento prospectivo de uma hipótese confirmatória para essas observações. Os pilotos de oito e quatro episódios foram conduzidos com instrumentos diferentes e não foram agrupados em uma análise única.

## 3. Metodologia

Os experimentos simularam tarefas de aprovação de transações, com eventos de política autorizados e decisões binárias de aprovar ou rejeitar. Cada episódio representou uma sequência independente, mas as decisões dentro de um mesmo episódio eram observações correlacionadas. Não tratamos cada turno como uma amostra independente.

O piloto de segunda versão utilizou oito episódios, com dezoito turnos em cada episódio. Foram comparadas quatro condições com decisões reais de GPT e uma quinta condição derivada de uma proteção determinística.

O piloto temporal de terceira versão utilizou quatro episódios, também com dezoito turnos. Foram cinco condições de decisão GPT e uma sexta condição derivada. O modelo registrado nas respostas foi GPT seis ponto um Terra.

O instrumento temporal avaliou dois tipos de situação. Na revogação de regra antiga, uma restrição anteriormente válida deixa de impedir determinada ação. Na aplicação de regra nova, uma restrição recém-autorizada passa a impedir uma ação. As respostas esperadas foram calculadas separadamente dos dados enviados ao modelo.

Os métodos comparados incluíram o histórico integral, uma janela de contexto recente, a compactação recursiva feita por GPT e um registro externo com a política atualmente válida. O piloto temporal também incluiu um arquivo de restrições tipadas adaptado. Esse arquivo não corresponde à implementação completa de Knowledge Triage. Uma proteção determinística foi aplicada à resposta do registro externo, sem gerar nova chamada ao modelo.

A auditoria de evidências conferiu identificadores de respostas, arquivos originais do GitHub Actions, hashes criptográficos e integridade dos registros. No piloto temporal, foram recuperadas 432 observações pontuadas, 360 decisões genuínas do modelo e vinte compactações reais. As outras 72 observações eram decisões derivadas da proteção determinística.

O workflow original do piloto temporal terminou com falha na etapa de revisão automatizada. O erro foi identificado como ausência de uma resposta de revisão aceitável. Isso não apaga os dados empíricos recuperados, mas impede classificar a execução original como inteiramente bem-sucedida.

Também foram verificados seis pares de documentos públicos do ecossistema Python e Rust com relações explícitas de substituição. A proveniência das fontes foi confirmada, mas esses documentos não constituem tarefas experimentais adjudicadas por especialistas humanos.

Finalmente, a auditoria do componente TypeCompact utilizou a revisão imutável do código original de Knowledge Triage e a amostra pública de 327 arquivos. Foram testados quatro orçamentos relativos: 25, 50, 75 e 100 por cento do tamanho original estimado. A retenção literal das linhas que o classificador original reconheceu como restrições foi medida somente nos casos viáveis. Essa métrica não equivale à validação semântica independente.

## 4. Resultados

### 4.1. Piloto com oito episódios

O histórico completo acertou 144 de 144 decisões, correspondendo a cem por cento. A janela recente acertou 105 de 144 decisões, ou 72,9 por cento. A sumarização recursiva acertou 144 de 144. O registro externo de políticas também acertou 144 de 144. A proteção derivada do registro igualmente apresentou 144 acertos, mas não constitui um conjunto independente de decisões GPT.

A janela recente produziu 25 aprovações indevidas entre 88 oportunidades de rejeição e catorze rejeições indevidas. As outras condições não apresentaram esses erros.

A diferença observada entre sumarização recursiva e registro de políticas, no contraste exploratório de aprovações inseguras, foi zero em todos os oito episódios. Não se observou vantagem de um método sobre o outro.

### 4.2. Piloto temporal com quatro episódios

Histórico completo, sumarização recursiva, arquivo tipado adaptado e registro temporal de políticas acertaram, cada um, 72 de 72 decisões. A proteção derivada também obteve 72 acertos, reutilizando as decisões do registro.

A janela recente acertou 52 de 72 decisões, ou aproximadamente 72,2 por cento.

Cada condição continha dezesseis testes de revogação de regras antigas e dezesseis testes de aplicação de novas restrições. Nenhuma das condições apresentou erros nessas duas categorias específicas. Os vinte erros da janela recente ocorreram em casos de controle.

Em cada episódio, a diferença exploratória entre arquivo tipado adaptado e registro de políticas, nos testes de revogação após compactações, foi zero. A sequência observada foi: zero, zero, zero e zero.

O workflow original terminou com falha na revisão automatizada. A recuperação posterior verificou as observações, mas não transformou retroativamente a execução original em sucesso nem forneceu revisores humanos independentes.

### 4.3. Auditoria do componente TypeCompact

Foram avaliados 327 arquivos públicos em quatro orçamentos, totalizando 1.308 medições.

Com orçamento de 25 por cento, 308 arquivos foram viáveis e dezenove retornaram compactação inviável.

Com orçamento de 50 por cento, 323 arquivos foram viáveis e quatro retornaram compactação inviável.

Com orçamento de 75 por cento, 326 arquivos foram viáveis e um retornou compactação inviável.

Com orçamento de cem por cento, os 327 arquivos foram viáveis.

Entre os arquivos viáveis que continham restrições reconhecidas pelo classificador regex original, a retenção literal dessas restrições foi de cem por cento. Esse resultado é compatível com o próprio funcionamento do algoritmo, que procura preservar as restrições identificadas. Não prova que o classificador detectou todas as restrições semanticamente relevantes nem que o sistema é seguro.

### 4.4. Proveniência das fontes

Os seis pares externos de documentos Python e Rust passaram pela verificação de versões e identidades dos arquivos originais. Isso confirma a origem independente dos documentos, mas não confirma decisões de agentes, rótulos humanos ou regras de precedência entre autoridades.

## 5. Discussão

O resultado mais importante é o efeito de teto nos testes de substituição temporal. Todos os métodos avaliados acertaram as situações explícitas de revogação e de entrada em vigor de novas restrições.

A janela recente apresentou erros nos casos de controle, o que indica perda de informação relevante nesse ambiente sintético. Entretanto, os erros não demonstram uma falha específica na interpretação de revogações.

O arquivo tipado adaptado e o registro temporal de políticas tiveram o mesmo desempenho nas situações observadas. O registro externo recebeu informações explícitas sobre o estado atual da política. Portanto, a comparação não isola perfeitamente a arquitetura de memória da quantidade e da qualidade das informações disponíveis.

As atualizações de política eram claras e estruturadas. Isso pode ter tornado os casos relativamente fáceis para o modelo testado. A amostra também foi pequena e inteiramente sintética.

Uma comparação futura precisará equilibrar acesso às fontes, orçamento de contexto e condições de autoridade. Também deverá incluir ambiguidades, evidências atrasadas, conflitos entre emissores e decisões de referência produzidas por avaliadores humanos independentes.

A auditoria do TypeCompact demonstra que a preservação rígida de restrições pode ultrapassar o orçamento de compactação. O próprio operador original sinaliza essa situação como compactação inviável. Não devemos contar esses casos como compactações seguras bem-sucedidas.

## 6. Limitações

A validade dos cenários é limitada porque transações e políticas foram simuladas, e os documentos públicos ainda não foram convertidos em casos adjudicados independentemente.

A comparação entre métodos também tem limitações: o registro de políticas possui acesso explícito ao estado atual, e o arquivo tipado adaptado não reproduz todo o framework original de Knowledge Triage.

Do ponto de vista estatístico, quatro e oito episódios independentes não sustentam uma conclusão confirmatória. Diferenças iguais a zero em amostras pequenas não demonstram equivalência.

Do ponto de vista operacional, versões de modelos hospedados podem mudar. A revisão automatizada do piloto temporal falhou. Não existem dois pareceres humanos independentes concluídos.

A métrica de retenção literal de restrições depende do próprio classificador original e não valida segurança semântica. Por fim, a novidade científica permanece em aberto diante dos trabalhos Knowledge Triage e Supersede.

## 7. Reprodutibilidade e ética

As execuções originais e os arquivos de evidência estão documentados no repositório When Agent Memory Becomes Unsafe, de Daniel Raaid, no GitHub.

O piloto com oito episódios está associado à execução 43624782133. O piloto temporal está associado à execução 43640571248, que terminou com falha na revisão automatizada. A recuperação das observações ocorreu na execução 43643292807.

A verificação de documentos públicos ocorreu na execução 43652578796. A auditoria do componente TypeCompact ocorreu na execução 43652663710.

Todas as decisões experimentais utilizaram cenários sintéticos. Não reivindicamos estudo com participantes humanos nem certificação de segurança para aplicações reais. Ferramentas de inteligência artificial auxiliaram na elaboração do manuscrito e em pareceres consultivos, sem substituir revisão científica independente. O autor é responsável pela verificação das fontes, da originalidade e das conclusões.

O conjunto confirmatório privado não foi aberto por essas atividades.

## 8. Conclusão

Os dois pilotos com respostas reais de GPT e a auditoria do componente original de Knowledge Triage fornecem uma descrição reprodutível de resultados exploratórios.

Nos casos sintéticos explícitos de substituição temporal, não houve vantagem observada do registro de políticas ou do arquivo tipado adaptado sobre a sumarização recursiva. As condições apresentaram desempenho perfeito nos testes específicos de revogação e aplicação de novas restrições, revelando um limite importante do instrumento experimental.

O TypeCompact original apresentou estados de compactação inviável quando os orçamentos foram mais agressivos. Isso confirma a necessidade de registrar viabilidade separadamente da retenção de restrições.

O trabalho contribui como relato metodológico exploratório, mas não comprova superioridade de segurança, novidade científica ou validação confirmatória. A continuidade exige casos mais discriminativos, avaliação humana independente e uma comparação integral e metodologicamente equivalente com trabalhos anteriores.

## Referências bibliográficas

As referências principais são The Compaction Cliff in Long-Running AI Agent Memory, de Zerhoudi e colaboradores, publicado na CIKM em 2026; Supersede, de Patel, preprint de 2026; ACON, de Kang e colaboradores; LongMemEval, de Wu e colaboradores; e Lost in the Middle, de Liu e colaboradores. Os identificadores e endereços completos estão no manuscrito escrito disponível no GitHub.

Fim da leitura do artigo exploratório.
