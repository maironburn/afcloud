#!/bin/bash

KUBE_ROOT=/root/.kube

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
				kubectl delete pv "$1-pv"
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
					echo -e "\nPersistentVolumeClaim"
					echo -e "--------------------------\n"					
					kubectl --namespace="$NS" get pvc
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

else

	case "$1" in
	
			cc)
				
				FORMER=''
				CURRENT=''
				pushd .
				
				cd "$KUBE_ROOT"
				clear
				if [ `diff config config_solis | wc -l` -eq 0 ];then
					# configacion de k8s remota
					FORMER="config_solis"
					cp -v config_minikube config
					CURRENT="config_minikube"
				else
					# la config establecida es minikube local 
					FORMER="config_minikube"
					cp -v config_solis config
					CURRENT="config_solis"
				fi
				popd 
				echo "Se ha cambiado la configuracion de $FORMER -> $CURRENT"
				echo "Listando proyectos"
				kubectl get ns
			;;	
			
		  where)
			cd "$KUBE_ROOT"
			clear
			if [ `diff config config_solis | wc -l` -eq 0 ];then
				echo "Configuracion actual: config_solis"
			else
				echo "Configuracion actual: minikube local"
			fi
	esac
	
fi

