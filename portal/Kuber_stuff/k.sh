#!/bin/bash

if [ "$#" -eq 2 ];then

	NS="$1"
	ACTION="$2"
	INGRESS="$NS-ingress"
	SECRET=""
	echo "Namespace: $1, action: $2"
	echo "number of params: $#"

	case "$ACTION" in

		funde)

			kubectl delete namespace "$NS"

		;;
		funde_all)

		;;

		del_pv)
		
			for i in `kubectl get pv | tail -n +2 | awk '{print $1}'`;do
				kubectl delete pv "$i"
			 done
		;;
		
			ingress)

				kubectl --namespace="$NS" get ingress "$INGRESS" -ojson
			;;

			ns)
				kubectl get ns
				kubectl get pv
			;;

			info)
				clear
					echo -e "\n\nNS: $NS"
					echo -e "--------------------------\n"
					echo -e "\nHorizontalPodAutoscaler"
					echo -e "--------------------------\n"
					kubectl --namespace="$NS" get hpa
					echo -e "\nSecrets"
					echo -e "--------------------------\n"
					kubectl --namespace="$NS" get secrets
					echo -e "\nIngress"
					echo -e "--------------------------\n"
					kubectl --namespace="$NS" get ingress
					echo -e "\nDeployments"
					echo -e "--------------------------\n"
					kubectl --namespace="$NS" get deployments
					echo -e "\nServicios"
					echo -e "--------------------------\n"
					kubectl --namespace="$NS" get services

				;;


			 *)
			echo -ne "Parametros de uso:\n $SCRIPTNAME  { info | funde | funde_all | ns | ingress}\n" >&2

					exit 3
		;;

	esac

fi

