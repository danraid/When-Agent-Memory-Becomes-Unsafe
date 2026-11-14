# WAMBU-001 | Auditoria factual do piloto v2 | 2026-11-14

**Classificacao:** piloto exploratorio observado e integralmente executado; qualificado apenas para revisao de desenho. Nao e confirmacao cientifica, aprovacao academica nem submissao.

## Proveniencia e integridade
- [Execucao 43624782133](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43624782133): completed/success, tentativa 1, 2026-11-14 18:07:04 a 18:22:52 UTC.
- [Job independent-pilot, ID 132538085232](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43624782133/job/132538085232): success. Suite de 71 testes, 1 skipped (ReportLab opcional).
- [Commit de origem a839aa30716a269115d83856689b6937de7e5aee](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/commit/a839aa30716a269115d83856689b6937de7e5aee).
- [Artefato original 14125784623](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43624782133/artifacts/14125784623), nome `wambu-v2-independent-pilot-43624782133`, 182361 bytes, 13 membros ZIP. SHA-256 verificado dos bytes originais: `114d3b4e0ea174f36471092565db88c10fbd6761e29d83f04e3d8c1375baf08e`, coincidente com a API e com o log de upload. Teste ZIP CRC: OK.
- As cinco entradas referenciadas pelos manifests internos (`empirical/compactions.json`, `empirical/observations.json`, `empirical/status.json`, `empirical/summary.json`, `advisory/reviewers.json`) passaram verificacoes independentes de tamanho e SHA-256. Os 720 prompts armazenados passaram recomputacao de hash.
- Sao 618 IDs de respostas de provedor distintos para 576 decisoes pagas, 40 compactacoes e 2 revisoes. Os 144 casos do braco `pinned_ledger_guard` reutilizam a resposta do braco `pinned_ledger` e nao constituem chamadas adicionais. O ledger declara 618 chamadas; custo `USD 3.8996073` e somente estimativa/reserva contabilistica, nao faturacao atestada pelo provedor. Os IDs sao consistentes no artefato, mas nao foram auditados por acesso direto ao provedor.

## Descricao dos oito episodios
O ZIP contem 8 episodios distintos, 18 passos por episodio, cinco condicoes pontuadas e cinco compactacoes recursivas por episodio. Sao 720 observacoes pontuadas, das quais 144 derivadas, 576 respostas de decisao de GPT e 40 compactacoes genuinas. Modelo registrado das decisoes e compactacoes: `gpt-6.1-terra`.

| Condicao | Acertos de 144 | Acuracia bruta | Aprovacoes indevidas entre 88 casos de rejeicao de referencia | Falsas rejeicoes |
| --- | ---: | ---: | ---: | ---: |
| full_history | 144 | 100% | 0/88 | 0 |
| recent_window | 105 | 72,9% | 25/88 | 14 |
| recursive_summary | 144 | 100% | 0/88 | 0 |
| pinned_ledger | 144 | 100% | 0/88 | 0 |
| pinned_ledger_guard (derivado) | 144 | 100% | 0/88 | 0 |

Contraste candidato, estritamente descritivo, apos ao menos duas compactacoes: media de `recursive_summary minus pinned_ledger` de risco de aprovacao indevida **0,0000** nos oito episodios; denominadores elegiveis por episodio: **7, 7, 8, 7, 8, 8, 6, 7**. Diferenca nula **nao demonstra equivalencia**. Sem p-value, IC ou teste confirmatorio. A unidade de independencia proposta e o episodio, nao cada observacao aninhada. A intervencao difere tambem na disponibilidade de informacao autoritativa, portanto os resultados nao estabelecem superioridade sob acesso equivalente a informacoes.

## Duas revisoes automatizadas
O ZIP registra dois pareceres distintos de `gpt-6-luna`, um de contrato JSON e outro metodologico, sobre 16 apresentacoes (4 casos pareados x 4 condicoes), sem rotulos de referencia. O parecer de contrato informa JSON valido em todas as 16 respostas; o metodologico alerta para confusao de acesso privilegiado a politicas, contextos desiguais e dependencia entre observacoes. **Sao pareceres automatizados, nao revisao independente por pares.**

**Defeito editorial detectado:** o codigo `study/review.py` seleciona amostra pareada por hash SHA-256, estratificada por profundidade (duas observacoes de profundidade inferior a 2 e duas de profundidade igual ou superior a 2). Entretanto o texto efetivamente enviado ao revisor descreve, incorretamente, `deterministic lexicographic first two cases per condition`. Por isso o parecer metodologico repete uma caracterizacao errada da amostragem. Corrigir a descricao em futura revisao de codigo/documentacao; nao reexecutar chamadas pagas automaticamente e preservar os pareceres originais historicos.

## Limites, confirmatorio e novidade
O arquivo `empirical/summary.json` declara `split=pilot`, `holdout_touched=false`, `private_seed_digest=null`, `scientifically_approved=false` e `submission_authorized=false`. O preflight do workflow verificou ausencia de arquivos de aprovacao e congelamento do protocolo. Este exame nao acessou semente privada ou amostras confirmatorias. O plano de 32 episodios segue **NAO AUTORIZADO / NAO CONGELADO**.

**Bloqueio de novidade permanece ativo:** [literature/HIGH_OVERLAP_PRIOR_ART_2026-11-14.md](../literature/HIGH_OVERLAP_PRIOR_ART_2026-11-14.md). O trabalho [The Compaction Cliff in Long-Running AI Agent Memory (CIKM 2026)](https://doi.org/10.1145/3799682.3840567) e a implementacao [Knowledge Triage](https://github.com/searchsim-org/cikm26-knowledge-triage) sobrepoem-se substancialmente a alegacoes gerais de retencao de regras sob compactacao. Uma questao potencialmente distinta, ainda nao comprovada, e **supersessao temporal de politicas** (revogacao, substituicao e mudanca de escopo). Exige comparador Knowledge Triage fiel ou alternativa simplificada devidamente rotulada, ablaçoes de informacao e orcamento de tokens, protocolo prospectivo e revisao humana antes de qualquer autorizacao confirmatoria.

**Decisao final:** integridade do artefato original e consistencia interna PASS; piloto de viabilidade executado, nao aprovado cientificamente; confirmatorio BLOQUEADO; nenhuma submissao a revista; nenhuma chamada paga reexecutada nesta auditoria.
