; ModuleID = '/home/tijl/code/llmO/results/extracted-ir/20260807_full_run-extracted-ir/ministral-3-14b-instruct-q4km/repeated_sort_cpp/input_extraction/assemble/input.bc'
source_filename = "/home/tijl/code/llmO/SUT/repeated_sort.cpp"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-redhat-linux-gnu"

%"struct.std::ranges::less" = type { i8 }
%"struct.std::identity" = type { i8 }

; Function Attrs: mustprogress uwtable
define i64 @repeated_sort(ptr noundef readonly %input, i64 noundef %input_length, i32 noundef %rounds) local_unnamed_addr #0 personality ptr @__gxx_personality_v0 {
entry:
  %cmp = icmp ne ptr %input, null
  %cmp2 = icmp ne i64 %input_length, 0
  %cmp588 = icmp sgt i32 %rounds, 0
  %or.cond = and i1 %cmp, %cmp2
  %or.cond = and i1 %or.cond, %cmp588
  br i1 %or.cond, label %for.body.lr.ph, label %return

for.body.lr.ph:
  %add.ptr.idx = shl nuw nsw i64 %input_length, 2
  %cmp.i.i.i.i.i.i.i.i.i.i = icmp ugt i64 %input_length, 1
  %cmp1.i.i.i.i.i.i.i.i.i.i = icmp eq i64 %input_length, 1
  %0 = tail call range(i64 0, 65) i64 @llvm.ctlz.i64(i64 %input_length, i1 true)
  %1 = shl nuw nsw i64 %0, 1
  %mul.i.i.i.i = sub nuw nsw i64 126, %1
  %div38 = lshr i64 %input_length, 1
  %rem = and i64 %input_length, 1
  %cmp11 = icmp eq i64 %rem, 0
  %wide.trip.count = zext nneg i32 %rounds to i64
  br label %for.body

for.body:
  %indvars.iv = phi i64 [ 0, %for.body.lr.ph ], [ %indvars.iv.next, %cond.end ]
  %total.090 = phi i64 [ 0, %for.body.lr.ph ], [ %add25, %cond.end ]
  %call5.i.i.i5.i = invoke noalias noundef nonnull ptr @_Znwm(i64 noundef %add.ptr.idx) #6
          to label %_ZNSt12_Vector_baseIiSaIiEE11_M_allocateEm.exit.i.i unwind label %lpad.i

_ZNSt12_Vector_baseIiSaIiEE11_M_allocateEm.exit.i.i:
  %cmp.i.i.i.i.i.i.i.i.i.i = icmp ugt i64 %input_length, 1
  br i1 %cmp.i.i.i.i.i.i.i.i.i.i, label %if.then.i.i.i.i.i.i.i.i.i.i, label %if.else.i.i.i.i.i.i.i.i.i.i

if.then.i.i.i.i.i.i.i.i.i.i:
  call void @llvm.memcpy.p0.p0.i64(ptr nonnull align 4 %call5.i.i.i5.i, ptr nonnull align 4 %input, i64 %add.ptr.idx, i1 false)
  br label %invoke.cont

if.else.i.i.i.i.i.i.i.i.i.i:
  br i1 %cmp1.i.i.i.i.i.i.i.i.i.i, label %if.then2.i.i.i.i.i.i.i.i.i.i, label %invoke.cont

if.then2.i.i.i.i.i.i.i.i.i.i:
  %2 = load i32, ptr %input, align 4, !tbaa !5
  store i32 %2, ptr %call5.i.i.i5.i, align 4, !tbaa !5
  br label %invoke.cont

invoke.cont:
  %add.ptr.i.i = getelementptr inbounds nuw i8, ptr %call5.i.i.i5.i, i64 %add.ptr.idx
  %4 = getelementptr i32, ptr %call5.i.i.i5.i, i64 %div38
  %cmp11 = icmp eq i64 %rem, 0
  %cmp1.i.i.i.i.i.i.i.i.i.i = icmp eq i64 %input_length, 1
  %cmp.i.i.i.i.i.i.i.i.i.i = icmp ugt i64 %input_length, 1

  ; Optimized in-place sort using insertion sort for small arrays (<= 16 elements)
  %len = trunc nsw i64 %input_length to i32
  %is_small = icmp ule i32 %len, 16
  br i1 %is_small, label %insertion_sort, label %introsort

insertion_sort:
  %i.0 = phi i32 [ 1, %insertion_sort.cond ], [ %i.1, %insertion_sort.body ]
  %j.0 = phi i32 [ 0, %insertion_sort.cond ], [ %j.1, %insertion_sort.body ]
  %key.0 = phi i32 [ undef, %insertion_sort.cond ], [ %key, %insertion_sort.body ]
  %cmp.i = icmp uge i32 %i.0, %len
  br i1 %cmp.i, label %insertion_sort.cond, label %insertion_sort.body

insertion_sort.body:
  %idx.i = getelementptr inbounds i32, ptr %call5.i.i.i5.i, i64 %i.0
  %key = load i32, ptr %idx.i, align 4, !tbaa !5
  %j.1 = phi i32 [ %j.0, %insertion_sort.body.preheader ], [ %j.2, %insertion_sort.body ]
  %cmp.j = icmp ugt i32 %j.1, 0
  br i1 %cmp.j, label %insertion_sort.body.preheader, label %insertion_sort.body.end

insertion_sort.body.preheader:
  %idx.j = getelementptr inbounds i32, ptr %call5.i.i.i5.i, i64 %j.1
  %val.j = load i32, ptr %idx.j, align 4, !tbaa !5
  %cmp.key.val = icmp sgt i32 %val.j, %key
  br i1 %cmp.key.val, label %insertion_sort.body.shift, label %insertion_sort.body.no_shift

insertion_sort.body.shift:
  %idx.shift = getelementptr inbounds i32, ptr %call5.i.i.i5.i, i64 %j.1
  %idx.shift.next = getelementptr inbounds i32, ptr %call5.i.i.i5.i, i64 %j.1, i64 1
  %val.shift = load i32, ptr %idx.shift, align 4, !tbaa !5
  store i32 %val.shift, ptr %idx.shift.next, align 4, !tbaa !5
  %j.2 = add nuw i32 %j.1, -1
  br label %insertion_sort.body

insertion_sort.body.no_shift:
  %idx.store = getelementptr inbounds i32, ptr %call5.i.i.i5.i, i64 %j.1
  store i32 %key, ptr %idx.store, align 4, !tbaa !5
  br label %insertion_sort.body.end

insertion_sort.body.end:
  %i.1 = add nuw i32 %i.0, 1
  br label %insertion_sort.body

insertion_sort.cond:
  %cond = phi i32 [ %len, %insertion_sort.body ], [ 1, %insertion_sort.cond ]
  br label %cond.end

introsort:
  invoke void @_ZSt16__introsort_loopIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEElNS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SE_SG_T1_(ptr nonnull %call5.i.i.i5.i, ptr nonnull %add.ptr.i.i, i64 noundef %mul.i.i.i.i, ptr null, ptr null)
          to label %.noexc unwind label %lpad7

.noexc:
  invoke void @_ZSt22__final_insertion_sortIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEENS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SE_SG_(ptr nonnull %call5.i.i.i5.i, ptr nonnull %add.ptr.i.i, ptr null, ptr null)
          to label %_ZNKSt6ranges9__sort_fnclITkNS_19random_access_rangeERSt6vectorIiSaIiEENS_4lessESt8identityQ8sortableIDTclsr6ranges8__accessE7__beginclsr3stdE7declvalIRT_EEEET0_T1_EEENSt13__conditionalIX14borrowed_rangeIS8_EEE4typeISA_NS_8danglingEEEOS8_SB_SC_.exit unwind label %lpad7

_ZNKSt6ranges9__sort_fnclITkNS_19random_access_rangeERSt6vectorIiSaIiEENS_4lessESt8identityQ8sortableIDTclsr6ranges8__accessE7__beginclsr3stdE7declvalIRT_EEEET0_T1_EEENSt13__conditionalIX14borrowed_rangeIS8_EEE4typeISA_NS_8danglingEEEOS8_SB_SC_.exit:
  %4 = getelementptr i32, ptr %call5.i.i.i5.i, i64 %div38
  br i1 %cmp11, label %cond.true, label %cond.false

cond.true:
  %add.ptr.i = getelementptr i8, ptr %4, i64 -4
  %5 = load i32, ptr %add.ptr.i, align 4, !tbaa !5
  %conv = sext i32 %5 to i64
  %add.ptr.i46 = getelementptr inbounds nuw i32, ptr %call5.i.i.i5.i, i64 %div38
  %6 = load i32, ptr %add.ptr.i46, align 4, !tbaa !5
  %conv14 = sext i32 %6 to i64
  %add = add nsw i64 %conv14, %conv
  %div15 = sdiv i64 %add, 2
  %conv16 = trunc nsw i64 %div15 to i32
  br label %cond.end

cond.false:
  %7 = load i32, ptr %4, align 4, !tbaa !5
  br label %cond.end

cond.end:
  %cond = phi i32 [ %conv16, %cond.true ], [ %7, %cond.false ]
  %conv18 = sext i32 %cond to i64
  %add19 = add nsw i64 %total.090, %conv18
  %rem22 = urem i64 %indvars.iv, %input_length
  %add.ptr.i53 = getelementptr inbounds nuw i32, ptr %call5.i.i.i5.i, i64 %rem22
  %8 = load i32, ptr %add.ptr.i53, align 4, !tbaa !5
  %conv24 = sext i32 %8 to i64
  %add25 = add nsw i64 %add19, %conv24
  call void @_ZdlPvm(ptr noundef nonnull %call5.i.i.i5.i, i64 noundef %add.ptr.idx) #7
  %indvars.iv.next = add nuw nsw i64 %indvars.iv, 1
  %exitcond.not = icmp eq i64 %indvars.iv.next, %wide.trip.count
  br i1 %exitcond.not, label %return, label %for.body

lpad.i:
  %3 = landingpad { ptr, i32 }
          catch ptr null
  br label %ehcleanup

lpad7:
  %9 = landingpad { ptr, i32 }
          catch ptr null
  call void @_ZdlPvm(ptr noundef nonnull %call5.i.i.i5.i, i64 noundef %add.ptr.idx) #7
  br label %ehcleanup

ehcleanup:
  %.pn = phi { ptr, i32 } [ %3, %lpad.i ], [ %9, %lpad7 ]
  %exn.slot.0 = extractvalue { ptr, i32 } %.pn, 0
  %10 = call ptr @__cxa_begin_catch(ptr %exn.slot.0) #8
  call void @__cxa_end_catch()
  br label %return

return:
  %retval.0 = phi i64 [ 0, %ehcleanup ], [ 0, %entry ], [ %add25, %cond.end ]
  ret i64 %retval.0
}

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #1

declare i32 @__gxx_personality_v0(...)

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #1

declare ptr @__cxa_begin_catch(ptr) local_unnamed_addr

declare void @__cxa_end_catch() local_unnamed_addr

; Function Attrs: nobuiltin allocsize(0)
declare noundef nonnull ptr @_Znwm(i64 noundef) local_unnamed_addr #2

; Function Attrs: nobuiltin nounwind
declare void @_ZdlPvm(ptr noundef, i64 noundef) local_unnamed_addr #3

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #4

; Function Attrs: mustprogress uwtable
declare void @_ZSt16__introsort_loopIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEElNS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SE_SG_T1_(ptr, ptr, i64 noundef, ptr, ptr) local_unnamed_addr #0

; Function Attrs: mustprogress uwtable
declare void @_ZSt22__final_insertion_sortIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEENS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SE_SG_(ptr, ptr, ptr, ptr) local_unnamed_addr #0

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i64 @llvm.ctlz.i64(i64, i1 immarg) #5

attributes #0 = { mustprogress uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #2 = { nobuiltin allocsize(0) "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #3 = { nobuiltin nounwind "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #5 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #6 = { builtin allocsize(0) }
attributes #7 = { builtin nounwind }
attributes #8 = { nounwind }

!llvm.linker.options = !{}
!llvm.module.flags = !{!0, !1, !2}
!llvm.ident = !{!3}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 8, !"PIC Level", i32 2}
!2 = !{i32 7, !"uwtable", i32 2}
!3 = !{!"clang version 20.1.8 (CentOS 20.1.8-9.el10_2)"}
!4 = !{!"branch_weights", !"expected", i32 2000, i32 1}
!5 = !{!6, !6, i64 0}
!6 = !{!"int", !7, i64 0}
!7 = !{!"omnipotent char", !8, i64 0}
!8 = !{!"Simple C++ TBAA"}
!9 = distinct !{!9, !10, !11}
!10 = !{!"llvm.loop.mustprogress"}
!11 = !{!"llvm.loop.unroll.disable"}
