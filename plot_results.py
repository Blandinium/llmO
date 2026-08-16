#!/usr/bin/env python3
"""Generate publication/poster graphs from optimization result artifacts."""
from __future__ import annotations
import argparse, csv, hashlib, math
from pathlib import Path
try:
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.lines import Line2D
except ImportError as exc:
    raise SystemExit("Plotting dependencies are missing. Install them with: pip install -r requirements-plotting.txt") from exc
from poster_results import *

COLORS = {"valid":"#2a9d8f", "compile_or_assemble_failure":"#e76f51", "correctness_or_benchmark_failure":"#f4a261", "response_truncated":"#9b5de5", "context_insufficient":"#457b9d", "other_failure":"#777777"}
OUTCOME_LABELS = {"valid":"Valid", "compile_or_assemble_failure":"Compile / assemble", "correctness_or_benchmark_failure":"Correctness / benchmark", "response_truncated":"Truncated", "context_insufficient":"Insufficient context", "other_failure":"Other"}
MARKERS = ["o","s","^","D","P","X","v","*"]
MODEL_LABELS = {
    "qwen2-5-coder-14b-q4km":"Qwen2.5-Coder", "qwen3-14b-q4km":"Qwen3",
    "devstral-small-2-24b-q4km":"Devstral", "gemma-4-12b-it-qat-udq4xl":"Gemma",
    "ministral-3-14b-instruct-q4km":"Ministral", "gpt-oss-20b-mxfp4":"GPT-OSS",
    "llm-compiler-7b-q4km":"LLM-Compiler 7B", "llm-compiler-13b-q4km":"LLM-Compiler 13B",
}
def model_label(model): return MODEL_LABELS.get(model, model)

def format_multiplier(value):
    """Compact poster label for a positive speedup factor."""
    if value >= 1_000_000: return f"{value/1_000_000:.1f}M×"
    if value >= 1_000: return f"{value/1_000:.1f}k×"
    if value >= 10: return f"{value:.0f}×"
    return f"{value:.1f}×"

def prompt_coverage(rows):
    """Available prompt-demand observations per technique."""
    return {t:(sum(r["total_prompt_tokens_processed"] is not None for r in rows if r["technique"]==t),
               sum(r["technique"]==t for r in rows)) for t in TECHNIQUES}

def provenance_marker_style(source, color):
    """Marker styling only; provenance never transforms the plotted value."""
    if source == "estimated":
        return {"facecolors":"none", "edgecolors":color, "linewidths":1.4}
    return {"facecolors":color, "edgecolors":color, "linewidths":.7}

def configure():
    plt.rcParams.update({"font.size":11,"axes.titlesize":13,"axes.labelsize":12,"legend.fontsize":9,"figure.dpi":150,"savefig.dpi":300,"pdf.fonttype":42,"axes.spines.top":False,"axes.spines.right":False})
def save(fig, out, name):
    fig.savefig(out/f"{name}.pdf", bbox_inches="tight"); fig.savefig(out/f"{name}.png", bbox_inches="tight"); plt.close(fig)
def jitter(model): return (int(hashlib.sha1(model.encode()).hexdigest()[:4],16)/65535-.5)*.22

def reliability_overall(rows,out):
    counts=outcome_counts(rows); fig,ax=plt.subplots(figsize=(10,4.6)); left=np.zeros(4)
    for outcome in OUTCOMES:
        vals=np.array([counts[t][outcome]/sum(counts[t].values())*100 if counts[t] else 0 for t in TECHNIQUES])
        ax.barh(range(4),vals,left=left,color=COLORS[outcome],label=OUTCOME_LABELS[outcome])
        for i,v in enumerate(vals):
            if v>=6: ax.text(left[i]+v/2,i,f"{v:.0f}%\n({counts[TECHNIQUES[i]][outcome]})",ha="center",va="center",fontsize=8,color="white" if outcome not in {"correctness_or_benchmark_failure"} else "black")
        left+=vals
    ax.set(yticks=range(4),yticklabels=[TECHNIQUE_LABELS[t] for t in TECHNIQUES],xlabel="Share of optimization tasks (%)",xlim=(0,100)); ax.invert_yaxis(); ax.legend(ncol=3,bbox_to_anchor=(.5,-.2),loc="upper center"); fig.tight_layout(); save(fig,out,"reliability-overall")

def reliability_heatmap(rows,out):
    a=np.full((5,4),np.nan)
    for i,b in enumerate(BENCHMARKS):
      for j,t in enumerate(TECHNIQUES):
        x=[r for r in rows if r["benchmark"]==b and r["technique"]==t]
        if x:a[i,j]=100*sum(r["valid_candidate"] for r in x)/len(x)
    fig,ax=plt.subplots(figsize=(9,5)); im=ax.imshow(a,vmin=0,vmax=100,cmap="RdYlGn",aspect="auto")
    for i in range(5):
      for j in range(4): ax.text(j,i,"—" if np.isnan(a[i,j]) else f"{a[i,j]:.0f}%",ha="center",va="center",color="white" if not np.isnan(a[i,j]) and (a[i,j]<25 or a[i,j]>80) else "black",fontweight="bold")
    ax.set(xticks=range(4),xticklabels=[TECHNIQUE_LABELS[t] for t in TECHNIQUES],yticks=range(5),yticklabels=BENCHMARKS); fig.colorbar(im,ax=ax,label="Tasks producing a valid candidate (%)"); fig.tight_layout(); save(fig,out,"reliability-by-benchmark")

def dotplot(rows,out,name,field,ylabel,techniques=TECHNIQUES,reference_line=None,annotation=None,provenance_field=None):
    fig,ax=plt.subplots(figsize=(13,6)); colors=plt.cm.tab10.colors
    for bi,b in enumerate(BENCHMARKS):
      for ti,t in enumerate(techniques):
        vals=[r for r in rows if r["benchmark"]==b and r["technique"]==t and r[field] is not None]
        x=bi*5+ti
        for r in vals:
          style=provenance_marker_style(r.get(provenance_field),colors[ti]) if provenance_field else {"color":colors[ti]}
          ax.scatter(x+jitter(r["model"]),r[field],s=34,alpha=.78,**style)
        if vals: ax.scatter(x,np.median([r[field] for r in vals]),marker="_",s=300,linewidth=3,color="black",zorder=4)
      if bi: ax.axvline(bi*5-1,color="#dddddd",lw=1)
    center=(len(techniques)-1)/2
    ax.set_xticks([i*5+center for i in range(5)],BENCHMARKS); ax.set_ylabel(ylabel); ax.grid(axis="y",alpha=.22)
    if reference_line is not None:
      ax.axhline(reference_line,color="#b2182b",lw=2,ls="--",zorder=1,label="Model context limit (100%)")
    if annotation:
      ax.text(.01,.98,annotation,transform=ax.transAxes,ha="left",va="top",fontsize=10,
              bbox={"boxstyle":"round,pad=.35","facecolor":"white","edgecolor":"#888888","alpha":.92})
    handles=[Line2D([0],[0],marker='o',color='w',markerfacecolor=colors[i],label=TECHNIQUE_LABELS[t]) for i,t in enumerate(techniques)]+[Line2D([0],[0],marker='_',markersize=15,color='black',label='Median')]
    if reference_line is not None: handles.append(Line2D([0],[0],color="#b2182b",lw=2,ls="--",label="Model context limit (100%)"))
    if provenance_field:
      provenance=[Line2D([0],[0],marker='o',linestyle='none',markerfacecolor='#555555',markeredgecolor='#555555',label='Actual LLM usage'),
                  Line2D([0],[0],marker='o',linestyle='none',markerfacecolor='none',markeredgecolor='#555555',label='Preflight estimate')]
      fig.legend(handles=handles,ncol=len(handles),loc="lower center",bbox_to_anchor=(.5,-.02))
      ax.legend(handles=provenance,loc="upper right",title="Token data",frameon=True)
    else:
      ax.legend(handles=handles,ncol=len(handles),loc="upper center",bbox_to_anchor=(.5,-.14))
    fig.tight_layout(); save(fig,out,name)

def performance(rows,out):
    models=sorted({r["model"] for r in rows}); marks={m:MARKERS[i%len(MARKERS)] for i,m in enumerate(models)}; cols={m:plt.cm.tab10(i%10) for i,m in enumerate(models)}
    fig,axes=plt.subplots(1,5,figsize=(18,5),sharey=False)
    for ax,b in zip(axes,BENCHMARKS):
      ax.axhspan(.98,1.02,color="#aaaaaa",alpha=.22); ax.axhline(1,color="black",lw=1)
      vals=[]
      for ti,t in enumerate(TECHNIQUES):
       for r in rows:
        if r["benchmark"]==b and r["technique"]==t and r["valid_candidate"] and r["speedup_vs_o3"] is not None:
         ax.scatter(ti+jitter(r["model"]),r["speedup_vs_o3"],marker=marks[r["model"]],color=cols[r["model"]],s=40); vals.append(r["speedup_vs_o3"])
      ax.set_title(b); ax.set_xticks(range(4),[TECHNIQUE_LABELS[t].replace(" ","\n") for t in TECHNIQUES],fontsize=9); ax.grid(axis="y",alpha=.2)
      use_log=bool(vals and max(vals)/min(vals)>50)
      if use_log: ax.set_yscale("log")
      if ax is axes[0]: ax.set_ylabel("Speedup vs Clang -O3 (×)")
      if use_log:
       for ti,t in enumerate(TECHNIQUES):
        extreme=[r for r in rows if r["benchmark"]==b and r["technique"]==t and r["valid_candidate"] and (r["speedup_vs_o3"] or 0)>=10]
        if extreme:
         top=max(extreme,key=lambda r:r["speedup_vs_o3"]); mult=top["speedup_vs_o3"]
         ax.annotate(format_multiplier(mult),(ti+jitter(top["model"]),mult),xytext=(0,-15),textcoords="offset points",ha="center",fontsize=8,fontweight="bold")
    handles=[Line2D([0],[0],marker=marks[m],color='w',markerfacecolor=cols[m],label=model_label(m),markersize=7) for m in models]
    fig.legend(handles=handles,ncol=4,loc="lower center",bbox_to_anchor=(.5,-.08)); fig.tight_layout(); save(fig,out,"performance-vs-o3")

def model_summary(rows,out):
    models=sorted({r["model"] for r in rows}); fig,ax=plt.subplots(figsize=(11,5)); x=np.arange(len(models)); w=.34
    metrics=[("Valid candidate rate",lambda z:z["valid_candidate"]),(f">{NOISE_THRESHOLD_PERCENT:g}% faster than -O3 rate",lambda z:z["meaningfully_faster_than_o3"])]
    for i,(label,fn) in enumerate(metrics):
      vals=[]
      for m in models:
       rs=[r for r in rows if r["model"]==m]; vals.append(100*sum(fn(r) for r in rs)/len(rs) if rs else 0)
      ax.bar(x+(i-.5)*w,vals,w,label=label)
    ax.set_xticks(x,[model_label(m) for m in models],rotation=25,ha="right"); ax.set_ylabel("Successful tasks / all attempted tasks (%)"); ax.legend(); fig.tight_layout(); save(fig,out,"model-summary")

def main():
    p=argparse.ArgumentParser(); p.add_argument("--results",type=Path,default=Path("results")); p.add_argument("--output",type=Path,default=Path("poster-graphs"))
    for opt in ["matrix","naive","guided","ir","extracted-ir"]: p.add_argument(f"--{opt}-run")
    a=p.parse_args(); a.output.mkdir(parents=True,exist_ok=True)
    runs={"naive_cpp":discover_run(a.results,"naive-cpp",a.naive_run),"guided_cpp":discover_run(a.results,"guided-cpp",a.guided_run),"full_ir":discover_run(a.results,"llm-ir",a.ir_run),"extracted_ir":discover_run(a.results,"extracted-ir",a.extracted_ir_run)}
    matrix=discover_run(a.results,"final-matrix",a.matrix_run); print("Selected runs:"); [print(f"  {TECHNIQUE_LABELS[t]}: {x}") for t,x in runs.items()]; print(f"  Final matrix: {matrix}")
    rows,diag=normalize(runs,matrix); fields=list(rows[0]);
    with (a.output/"data.csv").open("w",newline="") as f: w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    counts=outcome_counts(rows)
    for t in TECHNIQUES:
      rs=[r for r in rows if r["technique"]==t]; print(f"\n{TECHNIQUE_LABELS[t]}:\n  expected tasks: {len({r['model'] for r in rs}) * len(BENCHMARKS)}\n  found: {len(rs)}\n  classifications: {dict(counts[t])}")
      print(f"  missing: {diag['missing'][t] or 'none'}; duplicates: {diag['duplicates'][t] or 'none'}")
      print(f"  missing timing: {sum(r['llm_seconds'] is None for r in rs)}; missing prompt tokens: {sum(r['prompt_tokens'] is None and r['estimated_prompt_tokens'] is None for r in rs)}")
      assert sum(counts[t].values())==len(rs)
    invalid_success=[r for r in rows if not r["valid_candidate"] and (r["beats_o3"] or r["meaningfully_faster_than_o3"])]
    if invalid_success: raise RuntimeError(f"invalid candidates marked as performance successes: {invalid_success}")
    print("\nPrompt-token coverage:")
    for t in TECHNIQUES:
      rs=[r for r in rows if r["technique"]==t]; actual=sum(r["prompt_token_source"]=="actual" for r in rs); estimated=sum(r["prompt_token_source"]=="estimated" for r in rs)
      print(f"  {TECHNIQUE_LABELS[t]}: {actual}/{len(rs)} actual, {estimated}/{len(rs)} estimated, {len(rs)-actual-estimated}/{len(rs)} unavailable")
    guided=[r for r in rows if r["technique"]=="guided_cpp"]
    completed=sum((r["completed_optimization_passes"] or 0)>0 for r in guided)
    print(f"\nGuided C++ completed-pass validity:\n  total tasks: {len(guided)}\n  completed_optimization_passes > 0: {completed}\n  completed_optimization_passes == 0: {len(guided)-completed}")
    changed=[r for r in guided if bool(r["old_guided_valid_candidate"]) != bool(r["valid_candidate"])]
    print("  old/new validity changes:")
    for r in changed:
      print(f"    {r['model']} / {r['benchmark']}: status={r['status']}, old={r['old_guided_valid_candidate']}, new={r['valid_candidate']}, completed_passes={r['completed_optimization_passes']}, failure={r['failure_type'] or 'none'}")
    print("Guided C++ token recovery:")
    print(f"  discovered raw response files: {sum(r['guided_raw_response_file_count'] for r in guided)}")
    print(f"  unique raw calls with usage: {sum(r['raw_recovered_token_calls'] for r in guided)}")
    print(f"  structured-only fallback calls: {sum(r['structured_token_calls'] for r in guided)}")
    print(f"  still unavailable: {sum(r['prompt_token_source']=='unavailable' for r in guided)} tasks ({sum(r['unavailable_token_calls'] for r in guided)} calls)")
    print("\nIR tasks exceeding 100% context:")
    for t in ("full_ir","extracted_ir"):
      rs=[r for r in rows if r["technique"]==t and r["context_usage_percent"] is not None]; print(f"  {TECHNIQUE_LABELS[t]}: {sum(r['context_usage_percent']>100 for r in rs)}/{len(rs)}")
    print("Performance-success invariant: 0 invalid candidates classified as successful")
    print(f"\nValid source tasks absent from matrix: {diag['source_without_matrix'] or 'none'}\nMatrix candidates without source tasks: {diag['matrix_without_source'] or 'none'}")
    configure(); reliability_overall(rows,a.output); reliability_heatmap(rows,a.output)
    dotplot(rows,a.output,"cost-inference-time","llm_seconds","Total LLM CPU inference time per optimization task (seconds; this experiment)")
    coverage=prompt_coverage(rows); incomplete=[f"{TECHNIQUE_LABELS[t]} token coverage: {n}/{total} tasks" for t,(n,total) in coverage.items() if n<total]
    dotplot(rows,a.output,"cost-prompt-tokens","total_prompt_tokens_processed","Prompt-token demand per optimization task",annotation="\n".join(incomplete),provenance_field="prompt_token_source")
    dotplot(rows,a.output,"ir-context-pressure","context_usage_percent","Estimated prompt size (% of model context window)",techniques=["full_ir","extracted_ir"],reference_line=100)
    for suffix in ("pdf","png"):
      old=a.output/f"cost-context.{suffix}"
      if old.exists(): old.unlink()
    performance(rows,a.output); model_summary(rows,a.output)
    print("\nGenerated:"); [print(f"  {p.name}") for p in sorted(a.output.iterdir())]
if __name__=="__main__": main()
