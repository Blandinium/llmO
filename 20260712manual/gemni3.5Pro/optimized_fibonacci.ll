; ModuleID = '/home/tijl/code/llmO/SUT/fibonacci.cpp'
source_filename = "/home/tijl/code/llmO/SUT/fibonacci.cpp"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-redhat-linux-gnu"

declare i64 @llvm.ctlz.i64(i64, i1 immarg) #1

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none) uwtable
define i64 @fibonacci(i64 noundef %n) local_unnamed_addr #0 {
entry:
%cmp = icmp eq i64 %n, 0
br i1 %cmp, label %return, label %fast_doubling

fast_doubling:
%lz = tail call i64 @llvm.ctlz.i64(i64 %n, i1 true)
%start.bit = sub i64 63, %lz
br label %loop

loop:
%bit.idx = phi i64 [ %start.bit, %fast_doubling ], [ %bit.next, %loop ]
%a = phi i64 [ 0, %fast_doubling ], [ %a.next, %loop ]
%b = phi i64 [ 1, %fast_doubling ], [ %b.next, %loop ]

%b2 = shl i64 %b, 1
%b2.sub.a = sub i64 %b2, %a
%c = mul i64 %a, %b2.sub.a

%aa = mul i64 %a, %a
%bb = mul i64 %b, %b
%d = add i64 %aa, %bb

%n.shifted = lshr i64 %n, %bit.idx
%bit.val = and i64 %n.shifted, 1
%bit.is.1 = icmp ne i64 %bit.val, 0

%c.plus.d = add i64 %c, %d
%a.next = select i1 %bit.is.1, i64 %d, i64 %c
%b.next = select i1 %bit.is.1, i64 %c.plus.d, i64 %d

%done = icmp eq i64 %bit.idx, 0
%bit.next = sub i64 %bit.idx, 1
br i1 %done, label %exit, label %loop

exit:
br label %return

return:
%retval = phi i64 [ 0, %entry ], [ %a.next, %exit ]
ret i64 %retval
}

attributes #0 = { mustprogress nofree nosync nounwind willreturn memory(none) uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }

!llvm.linker.options = !{}
!llvm.module.flags = !{!0, !1, !2}
!llvm.ident = !{!3}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 8, !"PIC Level", i32 2}
!2 = !{i32 7, !"uwtable", i32 2}
!3 = !{!"clang version 20.1.8 (CentOS 20.1.8-9.el10_2)"}
