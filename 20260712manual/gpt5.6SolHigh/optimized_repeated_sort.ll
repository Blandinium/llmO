; ModuleID = '/home/tijl/code/llmO/SUT/repeated_sort.cpp'
source_filename = "/home/tijl/code/llmO/SUT/repeated_sort.cpp"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-redhat-linux-gnu"

%"struct.std::ranges::less" = type { i8 }
%"struct.std::identity" = type { i8 }

$*ZSt16__introsort_loopIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEElNS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SE_SG_T1* = comdat any

$*ZSt22__final_insertion_sortIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEENS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SE_SG* = comdat any

define internal void @__sift_down_i32(ptr nocapture %base, i64 %root, i64 %count) #10 {
entry:
%twice = shl i64 %root, 1
%child0 = add i64 %twice, 1
%has.child = icmp ult i64 %child0, %count
br i1 %has.child, label %loop, label %return

loop:
%r = phi i64 [ %root, %entry ], [ %chosen, %swap ]
%child = phi i64 [ %child0, %entry ], [ %next.child, %swap ]
%right = add i64 %child, 1
%has.right = icmp ult i64 %right, %count
br i1 %has.right, label %choose.right, label %chosen.ready

choose.right:
%lp = getelementptr inbounds i32, ptr %base, i64 %child
%rp = getelementptr inbounds i32, ptr %base, i64 %right
%lv = load i32, ptr %lp, align 4, !tbaa !5
%rv = load i32, ptr %rp, align 4, !tbaa !5
%right.larger = icmp slt i32 %lv, %rv
%chosen.right = select i1 %right.larger, i64 %right, i64 %child
br label %chosen.ready

chosen.ready:
%chosen = phi i64 [ %child, %loop ], [ %chosen.right, %choose.right ]
%rootp = getelementptr inbounds i32, ptr %base, i64 %r
%childp = getelementptr inbounds i32, ptr %base, i64 %chosen
%rootv = load i32, ptr %rootp, align 4, !tbaa !5
%childv = load i32, ptr %childp, align 4, !tbaa !5
%need.swap = icmp slt i32 %rootv, %childv
br i1 %need.swap, label %swap, label %return

swap:
store i32 %childv, ptr %rootp, align 4, !tbaa !5
store i32 %rootv, ptr %childp, align 4, !tbaa !5
%chosen.twice = shl i64 %chosen, 1
%next.child = add i64 %chosen.twice, 1
%has.next = icmp ult i64 %next.child, %count
br i1 %has.next, label %loop, label %return

return:
ret void
}

define internal void @__sort_i32(ptr nocapture %base, i64 %count) #10 {
entry:
%small = icmp ult i64 %count, 2
br i1 %small, label %return, label %heapify.preheader

heapify.preheader:
%half = lshr i64 %count, 1
br label %heapify

heapify:
%start.plus1 = phi i64 [ %half, %heapify.preheader ], [ %start, %heapify ]
%start = add i64 %start.plus1, -1
call void @__sift_down_i32(ptr %base, i64 %start, i64 %count)
%heap.done = icmp eq i64 %start, 0
br i1 %heap.done, label %sort.preheader, label %heapify

sort.preheader:
br label %sort.loop

sort.loop:
%end = phi i64 [ %count, %sort.preheader ], [ %last, %sort.cont ]
%last = add i64 %end, -1
%lastp = getelementptr inbounds i32, ptr %base, i64 %last
%firstv = load i32, ptr %base, align 4, !tbaa !5
%lastv = load i32, ptr %lastp, align 4, !tbaa !5
store i32 %lastv, ptr %base, align 4, !tbaa !5
store i32 %firstv, ptr %lastp, align 4, !tbaa !5
call void @__sift_down_i32(ptr %base, i64 0, i64 %last)
%sort.done = icmp eq i64 %last, 1
br i1 %sort.done, label %return, label %sort.cont

sort.cont:
br label %sort.loop

return:
ret void
}

define internal ptr @__partition_pivot_i32(ptr nocapture %first, ptr nocapture %last, i64 %count) #10 {
entry:
%a = getelementptr inbounds i32, ptr %first, i64 1
%half = lshr i64 %count, 1
%b = getelementptr inbounds i32, ptr %first, i64 %half
%c = getelementptr inbounds i32, ptr %last, i64 -1
%av = load i32, ptr %a, align 4, !tbaa !5
%bv = load i32, ptr %b, align 4, !tbaa !5
%cv = load i32, ptr %c, align 4, !tbaa !5
%a.lt.b = icmp slt i32 %av, %bv
br i1 %a.lt.b, label %a_less_b, label %a_ge_b

a_less_b:
%b.lt.c = icmp slt i32 %bv, %cv
br i1 %b.lt.c, label %choose_b, label %ab_else

ab_else:
%a.lt.c = icmp slt i32 %av, %cv
br i1 %a.lt.c, label %choose_c, label %choose_a

a_ge_b:
%a.lt.c.2 = icmp slt i32 %av, %cv
br i1 %a.lt.c.2, label %choose_a, label %age_else

age_else:
%b.lt.c.2 = icmp slt i32 %bv, %cv
br i1 %b.lt.c.2, label %choose_c, label %choose_b

choose_a:
%old.a = load i32, ptr %first, align 4, !tbaa !5
store i32 %av, ptr %first, align 4, !tbaa !5
store i32 %old.a, ptr %a, align 4, !tbaa !5
br label %partition.preheader

choose_b:
%old.b = load i32, ptr %first, align 4, !tbaa !5
store i32 %bv, ptr %first, align 4, !tbaa !5
store i32 %old.b, ptr %b, align 4, !tbaa !5
br label %partition.preheader

choose_c:
%old.c = load i32, ptr %first, align 4, !tbaa !5
store i32 %cv, ptr %first, align 4, !tbaa !5
store i32 %old.c, ptr %c, align 4, !tbaa !5
br label %partition.preheader

partition.preheader:
%pivot = load i32, ptr %first, align 4, !tbaa !5
br label %outer

outer:
%left.start = phi ptr [ %a, %partition.preheader ], [ %left.next, %swap ]
%right.start = phi ptr [ %last, %partition.preheader ], [ %right, %swap ]
br label %left.scan

left.scan:
%left = phi ptr [ %left.start, %outer ], [ %left.next.scan, %left.scan ]
%leftv = load i32, ptr %left, align 4, !tbaa !5
%left.less = icmp slt i32 %leftv, %pivot
%left.next.scan = getelementptr inbounds i32, ptr %left, i64 1
br i1 %left.less, label %left.scan, label %right.scan

right.scan:
%right.base = phi ptr [ %right.start, %left.scan ], [ %right, %right.scan ]
%right = getelementptr inbounds i32, ptr %right.base, i64 -1
%rightv = load i32, ptr %right, align 4, !tbaa !5
%pivot.less = icmp slt i32 %pivot, %rightv
br i1 %pivot.less, label %right.scan, label %compare

compare:
%crossed = icmp ult ptr %left, %right
br i1 %crossed, label %swap, label %return

swap:
store i32 %rightv, ptr %left, align 4, !tbaa !5
store i32 %leftv, ptr %right, align 4, !tbaa !5
%left.next = getelementptr inbounds i32, ptr %left, i64 1
br label %outer

return:
ret ptr %left
}

define i64 @repeated_sort(ptr noundef readonly %input, i64 noundef %input_length, i32 noundef %rounds) local_unnamed_addr #0 personality ptr @__gxx_personality_v0 {
entry:
%input.ok = icmp ne ptr %input, null
%length.ok = icmp ne i64 %input_length, 0
%rounds.ok = icmp sgt i32 %rounds, 0
%p0 = and i1 %input.ok, %length.ok
%valid = and i1 %p0, %rounds.ok
br i1 %valid, label %allocate, label %return.zero

allocate:
%bytes = shl nuw nsw i64 %input_length, 2
%buf = invoke noalias noundef nonnull ptr @_Znwm(i64 noundef %bytes)
to label %allocated unwind label %lpad.alloc

allocated:
call void @llvm.memcpy.p0.p0.i64(ptr nonnull align 4 %buf, ptr nonnull align 4 %input, i64 %bytes, i1 false)
%comp = alloca i8, align 1
%proj = alloca i8, align 1
%end = getelementptr inbounds i8, ptr %buf, i64 %bytes
%clz = call i64 @llvm.ctlz.i64(i64 %input_length, i1 true)
%twice.clz = shl nuw nsw i64 %clz, 1
%depth = sub nuw nsw i64 126, %twice.clz
call void @*ZSt16__introsort_loopIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEElNS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SE_SG_T1*(ptr %buf, ptr %end, i64 %depth, ptr %comp, ptr %proj)
call void @*ZSt22__final_insertion_sortIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEENS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SE_SG*(ptr %buf, ptr %end, ptr %comp, ptr %proj)
%half = lshr i64 %input_length, 1
%parity = and i64 %input_length, 1
%is.even = icmp eq i64 %parity, 0
br i1 %is.even, label %median.even, label %median.odd

median.even:
%left.idx = add i64 %half, -1
%left.ptr = getelementptr inbounds i32, ptr %buf, i64 %left.idx
%right.ptr = getelementptr inbounds i32, ptr %buf, i64 %half
%left.i32 = load i32, ptr %left.ptr, align 4, !tbaa !5
%right.i32 = load i32, ptr %right.ptr, align 4, !tbaa !5
%left.i64 = sext i32 %left.i32 to i64
%right.i64 = sext i32 %right.i32 to i64
%pair.sum = add nsw i64 %left.i64, %right.i64
%median.e = sdiv i64 %pair.sum, 2
br label %median.done

median.odd:
%middle.ptr = getelementptr inbounds i32, ptr %buf, i64 %half
%middle.i32 = load i32, ptr %middle.ptr, align 4, !tbaa !5
%median.o = sext i32 %middle.i32 to i64
br label %median.done

median.done:
%median = phi i64 [ %median.e, %median.even ], [ %median.o, %median.odd ]
%rounds64 = zext i32 %rounds to i64
%cycles = udiv i64 %rounds64, %input_length
%remainder = urem i64 %rounds64, %input_length
%no.cycles = icmp eq i64 %cycles, 0
br i1 %no.cycles, label %prefix.preheader, label %scan.preheader

prefix.preheader:
br label %prefix.loop

prefix.loop:
%pi = phi i64 [ 0, %prefix.preheader ], [ %pi.next, %prefix.loop ]
%psum = phi i64 [ 0, %prefix.preheader ], [ %psum.next, %prefix.loop ]
%pp = getelementptr inbounds i32, ptr %buf, i64 %pi
%pv32 = load i32, ptr %pp, align 4, !tbaa !5
%pv = sext i32 %pv32 to i64
%psum.next = add i64 %psum, %pv
%pi.next = add nuw nsw i64 %pi, 1
%prefix.done = icmp eq i64 %pi.next, %rounds64
br i1 %prefix.done, label %selected.done, label %prefix.loop

scan.preheader:
br label %scan.loop

scan.loop:
%si = phi i64 [ 0, %scan.preheader ], [ %si.next, %scan.loop ]
%sum.all = phi i64 [ 0, %scan.preheader ], [ %sum.all.next, %scan.loop ]
%sum.prefix = phi i64 [ 0, %scan.preheader ], [ %sum.prefix.next, %scan.loop ]
%sp = getelementptr inbounds i32, ptr %buf, i64 %si
%sv32 = load i32, ptr %sp, align 4, !tbaa !5
%sv = sext i32 %sv32 to i64
%sum.all.next = add i64 %sum.all, %sv
%prefix.candidate = add i64 %sum.prefix, %sv
%in.prefix = icmp ult i64 %si, %remainder
%sum.prefix.next = select i1 %in.prefix, i64 %prefix.candidate, i64 %sum.prefix
%si.next = add nuw nsw i64 %si, 1
%scan.done = icmp eq i64 %si.next, %input_length
%cycle.sum = mul i64 %cycles, %sum.all.next
%selected.all = add i64 %cycle.sum, %sum.prefix.next
br i1 %scan.done, label %selected.done, label %scan.loop

selected.done:
%selected.sum = phi i64 [ %psum.next, %prefix.loop ], [ %selected.all, %scan.loop ]
%median.sum = mul i64 %rounds64, %median
%result = add i64 %selected.sum, %median.sum
call void @_ZdlPvm(ptr noundef nonnull %buf, i64 noundef %bytes) #8
%one.round = icmp eq i64 %rounds64, 1
br i1 %one.round, label %return.result, label %probe.header

probe.header:
%probe.i = phi i64 [ 1, %selected.done ], [ %probe.next, %probe.ok ]
%probe.buf = invoke noalias noundef nonnull ptr @_Znwm(i64 noundef %bytes)
to label %probe.ok unwind label %lpad.probe

probe.ok:
call void @_ZdlPvm(ptr noundef nonnull %probe.buf, i64 noundef %bytes) #8
%probe.next = add nuw nsw i64 %probe.i, 1
%probes.done = icmp eq i64 %probe.next, %rounds64
br i1 %probes.done, label %return.result, label %probe.header

lpad.alloc:
%lp0 = landingpad { ptr, i32 }
catch ptr null
%exn0 = extractvalue { ptr, i32 } %lp0, 0
%catch0 = call ptr @__cxa_begin_catch(ptr %exn0) #9
call void @__cxa_end_catch()
br label %return.zero

lpad.probe:
%lp1 = landingpad { ptr, i32 }
catch ptr null
%exn1 = extractvalue { ptr, i32 } %lp1, 0
%catch1 = call ptr @__cxa_begin_catch(ptr %exn1) #9
call void @__cxa_end_catch()
br label %return.zero

return.result:
ret i64 %result

return.zero:
ret i64 0
}

define linkonce_odr void @*ZSt16__introsort_loopIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEElNS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SE_SG_T1*(ptr %__first.coerce, ptr %__last.coerce, i64 noundef %__depth_limit, ptr %__comp.coerce0, ptr %__comp.coerce1) local_unnamed_addr #10 comdat {
entry:
%first.int = ptrtoint ptr %__first.coerce to i64
%last.int = ptrtoint ptr %__last.coerce to i64
%bytes0 = sub i64 %last.int, %first.int
%count0 = ashr exact i64 %bytes0, 2
%large0 = icmp sgt i64 %count0, 16
br i1 %large0, label %loop, label %return

loop:
%last.cur = phi ptr [ %__last.coerce, %entry ], [ %cut, %continue ]
%count.cur = phi i64 [ %count0, %entry ], [ %left.count, %continue ]
%depth.cur = phi i64 [ %__depth_limit, %entry ], [ %depth.next, %continue ]
%depth.zero = icmp eq i64 %depth.cur, 0
br i1 %depth.zero, label %fallback, label %partition

fallback:
call void @__sort_i32(ptr %__first.coerce, i64 %count.cur)
br label %return

partition:
%depth.next = add nsw i64 %depth.cur, -1
%cut = call ptr @__partition_pivot_i32(ptr %__first.coerce, ptr %last.cur, i64 %count.cur)
call void @*ZSt16__introsort_loopIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEElNS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SE_SG_T1*(ptr %cut, ptr %last.cur, i64 %depth.next, ptr %__comp.coerce0, ptr %__comp.coerce1)
%cut.int = ptrtoint ptr %cut to i64
%left.bytes = sub i64 %cut.int, %first.int
%left.count = ashr exact i64 %left.bytes, 2
%continue.large = icmp sgt i64 %left.count, 16
br i1 %continue.large, label %continue, label %return

continue:
br label %loop

return:
ret void
}

define linkonce_odr void @*ZSt22__final_insertion_sortIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEENS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SE_SG*(ptr %__first.coerce, ptr %__last.coerce, ptr %__comp.coerce0, ptr %__comp.coerce1) local_unnamed_addr #10 comdat {
entry:
%first.int = ptrtoint ptr %__first.coerce to i64
%last.int = ptrtoint ptr %__last.coerce to i64
%bytes = sub i64 %last.int, %first.int
%count = ashr exact i64 %bytes, 2
%small = icmp ult i64 %count, 2
br i1 %small, label %return, label %outer

outer:
%i = phi i64 [ 1, %entry ], [ %i.next, %inserted ]
%ip = getelementptr inbounds i32, ptr %__first.coerce, i64 %i
%key = load i32, ptr %ip, align 4, !tbaa !5
br label %inner.test

inner.test:
%j = phi i64 [ %i, %outer ], [ %j.prev, %shift ]
%at.begin = icmp eq i64 %j, 0
br i1 %at.begin, label %insert, label %compare

compare:
%j.prev = add i64 %j, -1
%prevp = getelementptr inbounds i32, ptr %__first.coerce, i64 %j.prev
%prev = load i32, ptr %prevp, align 4, !tbaa !5
%less = icmp slt i32 %key, %prev
br i1 %less, label %shift, label %insert

shift:
%jp = getelementptr inbounds i32, ptr %__first.coerce, i64 %j
store i32 %prev, ptr %jp, align 4, !tbaa !5
br label %inner.test

insert:
%dest = getelementptr inbounds i32, ptr %__first.coerce, i64 %j
store i32 %key, ptr %dest, align 4, !tbaa !5
br label %inserted

inserted:
%i.next = add nuw nsw i64 %i, 1
%done = icmp eq i64 %i.next, %count
br i1 %done, label %return, label %outer

return:
ret void
}

declare i32 @__gxx_personality_v0(...)

declare ptr @__cxa_begin_catch(ptr) local_unnamed_addr

declare void @__cxa_end_catch() local_unnamed_addr

; Function Attrs: nobuiltin allocsize(0)
declare noundef nonnull ptr @_Znwm(i64 noundef) local_unnamed_addr #2

; Function Attrs: nobuiltin nounwind
declare void @_ZdlPvm(ptr noundef, i64 noundef) local_unnamed_addr #4

; Function Attrs: mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i64 @llvm.ctlz.i64(i64, i1 immarg) #5

attributes #0 = { mustprogress uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #2 = { nobuiltin allocsize(0) "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #3 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #5 = { mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #4 = { nobuiltin nounwind "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #8 = { builtin nounwind }
attributes #9 = { nounwind }
attributes #10 = { mustprogress nofree nosync nounwind willreturn memory(argmem: readwrite) "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }

!llvm.linker.options = !{}
!llvm.module.flags = !{!0, !1, !2}
!llvm.ident = !{!3}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 8, !"PIC Level", i32 2}
!2 = !{i32 7, !"uwtable", i32 2}
!3 = !{!"clang version 20.1.8 (CentOS 20.1.8-9.el10_2)"}
!5 = !{!6, !6, i64 0}
!6 = !{!"int", !7, i64 0}
!7 = !{!"omnipotent char", !8, i64 0}
!8 = !{!"Simple C++ TBAA"}
