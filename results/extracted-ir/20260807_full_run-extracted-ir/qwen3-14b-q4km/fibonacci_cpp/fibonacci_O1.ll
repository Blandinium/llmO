; ModuleID = '/home/tijl/code/llmO/SUT/fibonacci.cpp'
source_filename = "/home/tijl/code/llmO/SUT/fibonacci.cpp"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-redhat-linux-gnu"

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none) uwtable
define i64 @fibonacci(i64 noundef %n) local_unnamed_addr #0 {
entry:
  br label %tailrecurse

tailrecurse:                                      ; preds = %if.end, %entry
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

!llvm.linker.options = !{}
!llvm.module.flags = !{!0, !1, !2}
!llvm.ident = !{!3}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 8, !"PIC Level", i32 2}
!2 = !{i32 7, !"uwtable", i32 2}
!3 = !{!"clang version 20.1.8 (CentOS 20.1.8-9.el10_2)"}
