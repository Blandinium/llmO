; ModuleID = '/home/tijl/code/llmO/SUT/count_matches.cpp'
source_filename = "/home/tijl/code/llmO/SUT/count_matches.cpp"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-redhat-linux-gnu"

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(argmem: read) uwtable
define i64 @count_matches(ptr noundef readonly %allowed, i64 noundef %allowed_length, ptr noundef readonly %queries, i64 noundef %queries_length) local_unnamed_addr #0 {
entry:
  %qnull = icmp eq ptr %queries, null
  %qempty = icmp eq i64 %queries_length, 0
  %qbad = or i1 %qnull, %qempty
  br i1 %qbad, label %return, label %check.allowed

check.allowed:                                    ; preds = %entry
  ; Original semantics:
  ;  - (allowed == null && allowed_length != 0)  -> 0
  ;  - allowed_length == 0                       -> loop finds nothing -> 0
  ; Both collapse to returning 0 whenever allowed is null or empty.
  %aempty = icmp eq i64 %allowed_length, 0
  %anull = icmp eq ptr %allowed, null
  %abad = or i1 %aempty, %anull
  br i1 %abad, label %return, label %outer.preheader

outer.preheader:                                  ; preds = %check.allowed
  %vlen = and i64 %allowed_length, -8
  %hasvec = icmp ne i64 %vlen, 0
  br label %outer

outer:                                            ; preds = %outer.preheader, %latch
  %matches = phi i64 [ 0, %outer.preheader ], [ %matches.next, %latch ]
  %i = phi i64 [ 0, %outer.preheader ], [ %i.next, %latch ]
  %q.addr = getelementptr inbounds nuw i32, ptr %queries, i64 %i
  %q = load i32, ptr %q.addr, align 4, !tbaa !4
  %qv.ins = insertelement <4 x i32> poison, i32 %q, i64 0
  %qv = shufflevector <4 x i32> %qv.ins, <4 x i32> poison, <4 x i32> zeroinitializer
  br i1 %hasvec, label %vec.body, label %scalar.pre

vec.body:                                         ; preds = %outer, %vec.body
  %j = phi i64 [ %j.next, %vec.body ], [ 0, %outer ]
  %vp0 = getelementptr inbounds nuw i32, ptr %allowed, i64 %j
  %v0 = load <4 x i32>, ptr %vp0, align 4
  %vp1 = getelementptr inbounds nuw i8, ptr %vp0, i64 16
  %v1 = load <4 x i32>, ptr %vp1, align 4
  %c0 = icmp eq <4 x i32> %v0, %qv
  %c1 = icmp eq <4 x i32> %v1, %qv
  %cor = or <4 x i1> %c0, %c1
  %any = call i1 @llvm.vector.reduce.or.v4i1(<4 x i1> %cor)
  %j.next = add nuw i64 %j, 8
  %vdone = icmp eq i64 %j.next, %vlen
  %vexit = or i1 %any, %vdone
  br i1 %vexit, label %vec.exit, label %vec.body, !llvm.loop !8

vec.exit:                                         ; preds = %vec.body
  br i1 %any, label %latch, label %scalar.pre

scalar.pre:                                       ; preds = %outer, %vec.exit
  %rem.empty = icmp eq i64 %vlen, %allowed_length
  br i1 %rem.empty, label %latch, label %scalar.body

scalar.body:                                      ; preds = %scalar.pre, %scalar.body
  %k = phi i64 [ %k.next, %scalar.body ], [ %vlen, %scalar.pre ]
  %sp = getelementptr inbounds nuw i32, ptr %allowed, i64 %k
  %e = load i32, ptr %sp, align 4, !tbaa !4
  %seq = icmp eq i32 %e, %q
  %k.next = add nuw i64 %k, 1
  %sdone = icmp eq i64 %k.next, %allowed_length
  %sexit = or i1 %seq, %sdone
  br i1 %sexit, label %scalar.exit, label %scalar.body, !llvm.loop !9

scalar.exit:                                      ; preds = %scalar.body
  %sc = zext i1 %seq to i64
  br label %latch

latch:                                            ; preds = %vec.exit, %scalar.pre, %scalar.exit
  %contrib = phi i64 [ 1, %vec.exit ], [ 0, %scalar.pre ], [ %sc, %scalar.exit ]
  %matches.next = add nuw i64 %matches, %contrib
  %i.next = add nuw i64 %i, 1
  %odone = icmp eq i64 %i.next, %queries_length
  br i1 %odone, label %return, label %outer, !llvm.loop !10

return:                                           ; preds = %entry, %check.allowed, %latch
  %retval = phi i64 [ 0, %entry ], [ 0, %check.allowed ], [ %matches.next, %latch ]
  ret i64 %retval
}

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i1 @llvm.vector.reduce.or.v4i1(<4 x i1>) #1

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(argmem: read) uwtable "min-legal-vector-width"="128" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }

!llvm.linker.options = !{}
!llvm.module.flags = !{!0, !1, !2}
!llvm.ident = !{!3}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 8, !"PIC Level", i32 2}
!2 = !{i32 7, !"uwtable", i32 2}
!3 = !{!"clang version 20.1.8 (CentOS 20.1.8-9.el10_2)"}
!4 = !{!5, !5, i64 0}
!5 = !{!"int", !6, i64 0}
!6 = !{!"omnipotent char", !7, i64 0}
!7 = !{!"Simple C++ TBAA"}
!8 = distinct !{!8, !11, !12}
!9 = distinct !{!9, !11, !12}
!10 = distinct !{!10, !11}
!11 = !{!"llvm.loop.mustprogress"}
!12 = !{!"llvm.loop.unroll.disable"}
