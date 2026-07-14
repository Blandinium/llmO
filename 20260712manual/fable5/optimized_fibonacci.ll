; ModuleID = '/home/tijl/code/llmO/SUT/fibonacci.cpp'
source_filename = "/home/tijl/code/llmO/SUT/fibonacci.cpp"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-redhat-linux-gnu"

; Fast-doubling Fibonacci: O(log n) time, no recursion, no stack growth.
; Identities used (valid over Z, hence valid modulo 2^64 with wrapping
; i64 arithmetic, matching the value the original exponential recursion
; computes via repeated wrapping additions):
;   F(2k)   = F(k) * (2*F(k+1) - F(k))
;   F(2k+1) = F(k)^2 + F(k+1)^2
define i64 @fibonacci(i64 noundef %n) local_unnamed_addr #0 {
entry:
  %small = icmp ult i64 %n, 2
  br i1 %small, label %ret.small, label %init

init:                                             ; preds = %entry
  ; n >= 2 here, so ctlz operand is nonzero.
  %lz = tail call i64 @llvm.ctlz.i64(i64 %n, i1 true)
  %msb = sub nuw nsw i64 63, %lz
  br label %loop

loop:                                             ; preds = %loop, %init
  %i = phi i64 [ %msb, %init ], [ %i.dec, %loop ]
  %a = phi i64 [ 0, %init ], [ %a.next, %loop ]
  %b = phi i64 [ 1, %init ], [ %b.next, %loop ]
  ; c = F(2k) = a * (2b - a), d = F(2k+1) = a^2 + b^2
  %twob = shl i64 %b, 1
  %t = sub i64 %twob, %a
  %c = mul i64 %a, %t
  %a2 = mul i64 %a, %a
  %b2 = mul i64 %b, %b
  %d = add i64 %a2, %b2
  %shifted = lshr i64 %n, %i
  %bit = and i64 %shifted, 1
  %isset = icmp ne i64 %bit, 0
  %cd = add i64 %c, %d
  %a.next = select i1 %isset, i64 %d, i64 %c
  %b.next = select i1 %isset, i64 %cd, i64 %d
  %i.dec = add i64 %i, -1
  %done = icmp eq i64 %i, 0
  br i1 %done, label %ret.big, label %loop

ret.big:                                          ; preds = %loop
  ret i64 %a.next

ret.small:                                        ; preds = %entry
  ret i64 %n
}

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i64 @llvm.ctlz.i64(i64, i1 immarg) #1

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(none) uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }

!llvm.linker.options = !{}
!llvm.module.flags = !{!0, !1, !2}
!llvm.ident = !{!3}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 8, !"PIC Level", i32 2}
!2 = !{i32 7, !"uwtable", i32 2}
!3 = !{!"clang version 20.1.8 (CentOS 20.1.8-9.el10_2)"}
