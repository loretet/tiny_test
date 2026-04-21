Tiny test case for Neko ABL simulations that can be run on a very small number of cores. Updated continually as Neko changes.

For time-varying b.c.'s:

Neumann
```
...
    u%compute => user_compute
    u%neumann_conditions => neumann_update
...   
subroutine user_compute(time)
      type(time_state_t), intent(in) :: time
      real(kind=rp), pointer :: bc_value

      bc_value => neko_const_registry%get_real_scalar("bc_value")

      bc_value = scalar_bc(time)

   end subroutine user_compute

  subroutine neumann_update(fields, bc, time)
    type(field_list_t), intent(inout) :: fields
    type(field_dirichlet_t), intent(in) :: bc
    type(time_state_t), intent(in) :: time
    type(field_t), pointer :: flux
    integer i

    flux => fields%get_by_name("temperature")

    do i = 1, bc%msk(0)
       flux%x(bc%msk(i), 1, 1, 1) = scalar_bc(time)
    end do
    if (neko_bcknd_device .eq. 1) then
       call device_memcpy(flux%x, flux%x_d, flux%size(), &
                     host_to_device, sync=.false.)
    end if

  end subroutine neumann_update

     function scalar_bc(time) result(bc)
      type(time_state_t), intent(in) :: time
      real(kind=rp) :: bc

      bc = 0.05 - 0.01*time%t

   end function scalar_bc
```

Dirichlet:
```
...

    user%compute => user_compute
    user%dirichlet_conditions => dirichlet_update

...   

subroutine user_compute(time)
      type(time_state_t), intent(in) :: time
      real(kind=rp), pointer :: bc_value

      bc_value => neko_const_registry%get_real_scalar("bc_value")

      bc_value = scalar_bc(time)

   end subroutine user_compute

  subroutine dirichlet_update(fields, bc, time)
    type(field_list_t), intent(inout) :: fields
    type(field_dirichlet_t), intent(in) :: bc
    type(time_state_t), intent(in) :: time
    integer i

      if (fields%items(1)%ptr%name .eq. "temperature") then

       associate(s => fields%items(1)%ptr)
            do i = 1, bc%msk(0)
               s%x(bc%msk(i), 1, 1, 1) = scalar_bc(time)
            end do
            if (neko_bcknd_device .eq. 1) then
               call device_memcpy(s%x, s%x_d, s%size(), &
                     host_to_device, sync=.false.)
            end if
         end associate
      end if
   end subroutine dirichlet_update   

function scalar_bc(time) result(bc)
      type(time_state_t), intent(in) :: time
      real(kind=rp) :: bc

      bc = 265.0_rp - 0.25_rp/3600.0_rp*time%t

   end function scalar_bc
```
