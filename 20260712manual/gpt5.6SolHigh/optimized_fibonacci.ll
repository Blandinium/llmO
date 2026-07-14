; ModuleID = '/home/tijl/code/llmO/SUT/fibonacci.cpp'
source_filename = "/home/tijl/code/llmO/SUT/fibonacci.cpp"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-redhat-linux-gnu"

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none) uwtable
define i64 @fibonacci(i64 noundef %n) local_unnamed_addr #0 {
entry:
%small = icmp ult i64 %n, 2
br i1 %small, label %return, label %setup

setup:
%leading.zeros = tail call i64 @llvm.ctlz.i64(i64 %n, i1 true)
%top.bit = sub i64 63, %leading.zeros
br label %loop

loop:
%bit = phi i64 [ %top.bit, %setup ], [ %next.bit, %latch ]
%a = phi i64 [ 0, %setup ], [ %a.next, %latch ]
%b = phi i64 [ 1, %setup ], [ %b.next, %latch ]
%twice.b = shl i64 %b, 1
%two.b.minus.a = sub i64 %twice.b, %a
%d = mul i64 %a, %two.b.minus.a
%a.square = mul i64 %a, %a
%b.square = mul i64 %b, %b
%e = add i64 %a.square, %b.square
%d.plus.e = add i64 %d, %e
%shifted = lshr i64 %n, %bit
%bit.set = trunc i64 %shifted to i1
%a.next = select i1 %bit.set, i64 %e, i64 %d
%b.next = select i1 %bit.set, i64 %d.plus.e, i64 %e
%done = icmp eq i64 %bit, 0
br i1 %done, label %return, label %latch

latch:
%next.bit = add i64 %bit, -1
br label %loop

return:
%result = phi i64 [ %n, %entry ], [ %a.next, %loop ]
ret i64 %result
}

declare i64 @llvm.ctlz.i64(i64, i1 immarg) #1

attributes #0 = { mustprogress nofree nosync nounwind willreturn memory(none) uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }

!llvm.linker.options = !{}
!llvm.module.flags = !{!0, !1, !2}
!llvm.ident = !{!3}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 8, !"PIC Level", i32 2}
!2 = !{i32 7, !"uwtable", i32 2}
!3 = !{!"clang version 20.1.8 (CentOS 20.1.8-9.el10_2)"}
