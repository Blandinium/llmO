You are a compiler and LLVM IR optimization assistant. Return only the requested IR module.<|im_end|>
<|im_start|>user
You are an expert LLVM IR performance engineer.
The following LLVM IR module is invalid according to the LLVM verifier.

Task: repair the validity of the module.
- Repair validity only.
- Preserve the intended transformation and external ABI.
- Return one complete raw LLVM module with no Markdown or explanation.

LLVM version: 20.1.8

Verifier error output:
opt: /home/tijl/code/llmO/results/llm-ir/20260807_full_run-ir/llm-compiler-7b-q4km/fibonacci_cpp/extracted.ll:1:1: error: expected top-level entity
You are a compiler and LLVM IR optimization assistant. Return only the requested IR module.<|im_end|>
^


Invalid IR:
You are a compiler and LLVM IR optimization assistant. Return only the requested IR module.<|im_end|>
<|im_start|>user
You are an expert LLVM IR performance engineer.
Task: optimize the following LLVM IR module for maximum runtime performance.

Only rewrite the module when you identify a concrete optimization that is
unlikely to be recovered automatically by LLVM -O3. If no such safe
transformation exists, return the original module unchanged.

Prioritize:
1. Algorithmic improvements.
2. Better data structures.
3. Reduced allocation or copying.
4. Removal of unnecessary library/runtime work.
5. Safe specialization based only on guaranteed semantics.
6. Only then low-level loop or SSA transformations.

De-emphasize transformations LLVM already performs reliably, such as:
- ordinary common-subexpression elimination
- routine branch simplification
- basic dead-code elimination
- trivial inlining
- simple loop cleanup

Warning: Do not manually expand standard-library implementations or replace concise library calls with larger hand-written IR unless there is a concrete algorithmic or allocation advantage.

Environment:
- LLVM/Clang version 20.1.8
- Input generated from C++ at -O1
- x86-64 target
- The target triple and datalayout must remain unchanged
- The exported ABI must remain unchanged

Hard requirements:
- Return one complete raw LLVM IR module.
- No Markdown, explanation, notes, or code fences.
- No prose before or after the module.

Input IR:
; ModuleID = '/home/tijl/code/llmO/SUT/fibonacci.cpp'
source_filename = "/home/tijl/code/llmO/SUT/fibonacci.cpp"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-redhat-linux-gnu"

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none) uwtable
define i64 @fibonacci(i64 noundef %n) local_unnamed_addr #0 {
entry:
   br label %tailrecurse

tailrecurse:                                       ; preds = %if.end, %entry
  %accumulator.tr = phi i64 [ 0, %entry ], [ %add, %if.end ]
  %n.tr = phi i64 [ %n, %entry ], [ %sub1, %if.end ]
  %cmp = icmp ult i64 %n.tr, 2
  br i1 %cmp, label %return, label %if.end

if.end:                                           ; preds = %tailrecurse
  %sub = add i64 %n.tr, -1
  %call = tail call i64 @fibonacci(i64 noundef %sub)
  %sub1 = add i64 %n.tr, -2
  %add = add i64 %accumulator.tr, %call
  br label %tailrecurse

return:                                           ; preds = %tailrecurse
  %accumulator.ret.tr = add i64 %accumulator.tr, %n.tr
  ret i64 %accumulator.ret.tr
}

attributes #0 = { mustprogress nofree nosync nounwind willreturn memory(none) uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }

!llvm.linker.options = !{!0}
!llvm.module.flags = !{!1, !2, !3}
!llvm.ident = !{!4}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 8, !"PIC Level", i32 2}
!2 = !{i32 7, !"PIE Level", i32 2}
!3 = !{i32 7, !"uwtable", i32 2}
!4 = !{!"clang version 20.1.8 (CentOS 20.1.8-9.el10_2)"}
</code>
