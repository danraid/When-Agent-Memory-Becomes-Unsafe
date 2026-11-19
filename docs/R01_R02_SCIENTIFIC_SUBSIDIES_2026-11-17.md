# WAMBU-001 | Subsídios para superar R01 e R02

**Versão:** 2026-11-17. **Escopo:** investigação exploratória com fonte verificável, sem validação final nem novos dados confirmatórios.  
**Autoridade:** decisão do autor na issue #50, que exige revisões.  
**Status destes anexos:** recursos de investigação e protocolos de coleta, **não evidências conclusivas**.

## R01: subsídios para validação naturalística de decisões

Fontes estruturadas:
- [Matriz original dos oito PRs](../protocol/P07D_REAL_CODE_CHANGE_MATRIX.json) identifica repositório, PR e norma inicialmente relacionada.
- [Triagem histórica](../protocol/P07E_HISTORICAL_SCOPE_TRIAGE.json) explica as cinco correspondências documentais provisórias e três pareamentos inadequados.
- [Registo por caso das provas ainda necessárias](../protocol/R01_EVENT_TIME_EVIDENCE_ACQUISITION_V1.json) explicita, para **todos os oito casos**, o histórico normativo, evidência de autoridade, exceções, momento decisório e decisão operacional ainda em falta.
- [Validador atual](../scripts/r01_qualify_public_policy_actions.py) impede o uso de votos de IA, estado merged/closed ou autoatestação como rótulos verdadeiros.

### Estratégia concreta de obtenção de evidência

1. **Congelar o instante da decisão.** Para cada PR documentar criação, revisão relevante e fecho, com carimbo UTC retirado da fonte original, nunca apenas data de consulta.
2. **Reconstruir norma histórica.** Consultar commit da norma cuja data anteceda cada instante. Guardar URL permanente, SHA do commit, hash do conteúdo e as linhas textuais pertinentes. A mera existência no Git não prova adoção ou vigência.
3. **Estabelecer a cadeia de autoridade.** Documentar quem tinha poder de aprovar, rejeitar, conceder exceção ou determinar aviso; distinguir regra proposta de regra vigente.
4. **Fixar ação observável.** Definir pedido, ator, alternativas de ação e informação disponível naquele instante. Não inferir que PR integrado = ação normativa permitida.
5. **Rever conflitos.** Agentes especializados podem propor interpretação, apontar fontes e recomendar abstenção; as suas respostas nunca são rotuladas como peritos humanos independentes. Guardar divergências sem consenso forçado.
6. **Admissão conservadora.** Se faltar vigência, autoridade ou exceção verificável, excluir o caso do denominador de precisão e documentar a razão.

### Percurso por casos

| ID | PR original | Prioridade de prova |
|---|---|---|
| 001 | [CPython #133080](https://github.com/python/cpython/pull/133080) | Exceção invocada à PEP 387, âmbito temporal e autoridade para a remoção C-API |
| 002 | [CPython #140345](https://github.com/python/cpython/pull/140345) | Avisos de depreciação da AST versus retirada efetiva |
| 003 | [CPython #130697](https://github.com/python/cpython/pull/130697) | Cronologia de aviso e vigência da regra Unicode C API |
| 004 | [CPython #112639](https://github.com/python/cpython/pull/112639) | Versões da política durante um PR prolongado e âmbito do API inspect |
| 005 | [Rust #87652](https://github.com/rust-lang/rust/pull/87652) | Outra norma anterior à RFC 2972, que ainda não fora adotada à data de fecho |
| 006 | [Rust #161002](https://github.com/rust-lang/rust/pull/161002) | Norma sobre atributo cold num ABI customizado, não norma sobre assembly naked |
| 007 | [Rust #159382](https://github.com/rust-lang/rust/pull/159382) | Norma específica para shim de implementação EII naked |
| 008 | [CPython #133654](https://github.com/python/cpython/pull/133654) | Procedimento de depreciação/remoção de variáveis globais e exceções |

**Critério de conclusão:** existência de casos com decisão operacional defensável, evidência temporal/autoritativa verificável, revisão documentada e separação do rótulo correto da entrada do agente. Hoje há **zero rótulos de decisão qualificados**. A substituição de examinadores por agentes simulados é explicitamente declarada e não constitui adjudicação humana independente.

## R02: subsídios para reprodução fiel do Knowledge Triage

Fontes:
- [Estudo original](https://doi.org/10.1145/3799682.3840567), conforme identificação bibliográfica registada no repositório.
- [Código original](https://github.com/searchsim-org/cikm26-knowledge-triage), commit fixado `a6ceb01a3368cee25ef7ebcf05ebdab8c9be24a4`.
- [Requisitos de fidelidade](../protocol/KNOWLEDGE_TRIAGE_REPLICATION_REQUIREMENTS.md).
- [Inventário verificável do que foi realmente executado](../scripts/r02_audit_original_kt_parity.py).
- [Matriz prospetiva de oito requisitos](../protocol/R02_ORIGINAL_KT_REPLICATION_EVIDENCE_V1.json), com prova exigida para cada componente.

### Trabalho reproduzível e dependências reais

| Etapa | Evidência indispensável | Estado |
|---|---|---|
| KT01: fonte original e ambiente | Git SHA, licenças, módulos e lockfile | Componentes fixados |
| KT02: classificador e cascata | Classes nativas, embeddings `octen-embedding-8b`, adjudicador `gpt-5.4-mini`, IDs e respostas | Sem execução integral |
| KT03: TypeCompact | Orçamento, tipos nativos, saída, `COMPACTION_UNSAFE` | Ensaios de componente |
| KT04: TypeDecompose | Partições, localidade e budget | Ensaios de componente |
| KT05: TypeRetrieve | Relevância e scope nativos, métricas do artigo | Adaptador lexical, não reprodução |
| KT06: SafetyMargin | Fonte imutável e trace de execução | Não executado |
| KT07: corpus e parâmetros originais | Dataset, divisão, tokenizer, budgets, scorer, seeds | Não reproduzido |
| KT08: comparação downstream | Fontes e orçamento idênticos, prompts, IDs, sidecar separado, estimativa por episódio | Não executado |

**Alternativa científica válida, caso os modelos/serviços originais não estejam disponíveis:** declarar `ADAPTED_KT_INSPIRED_COMPONENTS` e limitar a discussão a uma avaliação de componentes. Usar OpenRouter como substituto sem identidade e paridade demonstradas **não** autoriza chamar a experiência de réplica do método publicado.

### Contrato de comparação justa

Para um estudo comparativo novo, cada braço deve receber a **mesma sequência de eventos e documentos permitidos** até ao momento decisório, com controlo de orçamentos, modelo, temperatura e evaluator-sidecar. Resultados `COMPACTION_UNSAFE` e erros de fornecedor são analisados como falhas/ausências com denominador explícito, não descartados. Nenhuma hipótese confirmatória ou margem de equivalência será escolhida depois de ver o holdout.

## Reprodutibilidade e proibições

```sh
python -m unittest discover -s tests -p 'test_r01_r02_subsidies.py' -v
python -m scripts.check_r01_r02_subsidies --out runs/r01-r02/subsidy_contract.json
python -m scripts.r01_qualify_public_policy_actions --out runs/r01-r02/r01.json
python -m scripts.r02_audit_original_kt_parity --out runs/r01-r02/r02.json
```

Os dados originais, falhas, pareceres divergentes e resultados nulos permanecem preservados. Os verificadores apenas demonstram integridade e **ausência de promoção indevida**; não demonstram completude da investigação. Não aceder à amostra confirmatória nem submeter externamente sem autorização própria do autor.

**Próximo marco objetivamente elegível:** procurar e arquivar as fontes operacionais que faltam para os cinco pares documentais R01, e obter (ou justificar impossibilidade de obter) o runtime idêntico do classificador/cascata original R02. Só então repetir os testes e emitir um parecer com critérios comprováveis.
